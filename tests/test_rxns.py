import pandas as pd
import pytest
from m2p import PolyMaker
from rdkit import Chem

pm = PolyMaker()


@pytest.fixture
def vinyl():
    return pm.thermoplastic("C=C", DP=10, mechanism="vinyl").polymer[0]


@pytest.fixture
def RS_ester_reactants():
    poly_name = ["poly(RS-3-hydroxybutyrate)"]
    smiles = ["C[C@@H](O)CC(=O)O.C[C@H](O)CC(=O)O"]

    reactants = pd.DataFrame({"smiles": smiles}, index=poly_name)
    reactants["monomers"] = reactants.smiles.apply(
        lambda s: pm.get_monomers(s, stereochemistry=True)
    )

    return reactants


def calc_pm(smi):
    # Dict to count
    RS_list = []
    mol = Chem.MolFromSmiles(smi)

    for atom in mol.GetAtoms():
        try:
            chiral_center = atom.GetProp("_CIPCode")
            RS_list.append(chiral_center)
        except:
            pass

    # Zip together list to get neighbors and determine R vs M addition
    is_M_add = list(map(lambda t: t[0] == t[1], zip(*(RS_list, RS_list[1:]))))
    pm = sum(is_M_add) / len(is_M_add)

    return pm


def test_vinyl(vinyl):
    smile_vinyl = vinyl
    assert smile_vinyl == "CCCCCCCCCCCCCCCCCCCC"


def test_ester_stereo_iso(RS_ester_reactants):
    poly_df = pm.thermoplastic(
        RS_ester_reactants, DP=10, mechanism="ester_stereo", pm=1, verbose=False
    )
    pmeso = calc_pm(poly_df["polymer"][0])

    assert len(poly_df) == 1
    assert pmeso == 1


def test_ester_stereo_syn(RS_ester_reactants):
    poly_df = pm.thermoplastic(
        RS_ester_reactants, DP=10, mechanism="ester_stereo", pm=0, verbose=False
    )
    pmeso = calc_pm(poly_df["polymer"][0])
    pmeso

    assert len(poly_df) == 1
    assert pmeso == 0


def test_ester_stereo_a(RS_ester_reactants):
    poly_df = pm.thermoplastic(
        RS_ester_reactants, DP=10, mechanism="ester_stereo", pm=0.5, verbose=False
    )
    pmeso = calc_pm(poly_df["polymer"][0])
    pmeso

    assert len(poly_df) == 1
    assert 0 < pmeso and pmeso < 1


def test_df_pm_ester_stereo(RS_ester_reactants):
    RS_ester_reactants["pm"] = 1

    poly_df = pm.thermoplastic(
        RS_ester_reactants, DP=10, mechanism="ester_stereo", verbose=False
    )
    pmeso = calc_pm(poly_df["polymer"][0])
    pmeso

    assert len(poly_df) == 1
    assert pmeso == 1
