from unittest.mock import patch

import pandas as pd
from concordance import *
from pytest import raises, approx, fixture


@fixture
def dataset() -> pd.DataFrame:
    data = [
        [1, Classification.Ref, Classification.Ref, Outcome.TrueRef],
        [31, Classification.Ref, Classification.Ref, Outcome.BFailFilter],
        [2, Classification.Ref, Classification.Ref, Outcome.Masked],
        [3, Classification.Ref, Classification.Alt, Outcome.FalseAlt],
        [43, Classification.Ref, Classification.Alt, Outcome.BothFailFilter],
        [4, Classification.Ref, Classification.Null, Outcome.FalseNull],
        [5, Classification.Ref, Classification.Het, Outcome.Het],
        [6, Classification.Ref, Classification.Missing, Outcome.MissingPos],
        [7, Classification.Alt, Classification.Ref, Outcome.FalseRef],
        [37, Classification.Alt, Classification.Ref, Outcome.Masked],
        [8, Classification.Alt, Classification.Alt, Outcome.TrueAlt],
        [48, Classification.Alt, Classification.Alt, Outcome.AFailFilter],
        [38, Classification.Alt, Classification.Alt, Outcome.BFailFilter],
        [9, Classification.Alt, Classification.Alt, Outcome.DiffAlt],
        [10, Classification.Alt, Classification.Null, Outcome.FalseNull],
        [11, Classification.Alt, Classification.Het, Outcome.Het],
        [12, Classification.Alt, Classification.Missing, Outcome.MissingPos],
        [13, Classification.Null, Classification.Ref, Outcome.Null],
        [14, Classification.Null, Classification.Alt, Outcome.Null],
        [15, Classification.Null, Classification.Null, Outcome.Null],
        [16, Classification.Null, Classification.Het, Outcome.Null],
        [17, Classification.Null, Classification.Missing, Outcome.Null],
        [18, Classification.Het, Classification.Ref, Outcome.Het],
        [19, Classification.Het, Classification.Alt, Outcome.Het],
        [20, Classification.Het, Classification.Null, Outcome.Het],
        [21, Classification.Het, Classification.Het, Outcome.Het],
        [22, Classification.Het, Classification.Missing, Outcome.MissingPos],
        [23, Classification.Missing, Classification.Ref, Outcome.MissingPos],
        [24, Classification.Missing, Classification.Alt, Outcome.MissingPos],
        [25, Classification.Missing, Classification.Null, Outcome.MissingPos],
        [26, Classification.Missing, Classification.Het, Outcome.MissingPos],
        [27, Classification.Missing, Classification.Missing, Outcome.MissingPos],
    ]
    return pd.DataFrame(data, columns=COLUMNS)


class TestClassification:
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_variantIsNull(self, mocked_variant):
        mocked_variant.genotypes = [[-1]]

        actual = Classification.from_variant(mocked_variant)
        expected = Classification.Null

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_variantIsHomRef(self, mocked_variant):
        mocked_variant.genotypes = [[0, 0]]

        actual = Classification.from_variant(mocked_variant)
        expected = Classification.Ref

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_variantIsHet(self, mocked_variant):
        mocked_variant.genotypes = [[1, 0]]

        actual = Classification.from_variant(mocked_variant)
        expected = Classification.Het

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_variantIsHomAlt(self, mocked_variant):
        mocked_variant.genotypes = [[1, 1]]

        actual = Classification.from_variant(mocked_variant)
        expected = Classification.Alt

        assert actual == expected


class TestClassify:
    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_positionsDontMatch_raisesError(self, mocked_avariant, mocked_bvariant):
        classifier = Classifier()
        mocked_avariant.POS = 1
        mocked_bvariant.POS = 2

        with raises(IndexError):
            classifier.classify(mocked_avariant, mocked_bvariant)

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_positionInMask_returnsMasked(self, mocked_avariant, mocked_bvariant):
        mask = Bed()
        pos = 2
        chrom = "chr1"
        mask.positions = {chrom: {pos - 1}}
        classifier = Classifier(mask=mask)
        mocked_avariant.POS = pos
        mocked_avariant.CHROM = chrom
        mocked_avariant.genotypes = [[-1]]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[0]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Null, Classification.Ref, Outcome.Masked

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_aHasNull_returnsNull(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier()
        mocked_avariant.POS = pos
        mocked_avariant.genotypes = [[-1]]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[0]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Null, Classification.Ref, Outcome.Null

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_bothHaveNull_returnsNull(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier()
        mocked_avariant.POS = pos
        mocked_avariant.genotypes = [[-1, -1]]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[-1]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Null, Classification.Null, Outcome.Null

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_bHasNullOnly_returnsFalseNull(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier()
        mocked_avariant.POS = pos
        mocked_avariant.genotypes = [[1, -1]]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[-1]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Alt, Classification.Null, Outcome.FalseNull

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_bothRef_returnsTrueRef(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier()
        mocked_avariant.POS = pos
        mocked_avariant.genotypes = [[0, -1]]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[0, False]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Ref, Classification.Ref, Outcome.TrueRef

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_bIsRef_returnsFalseRef(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier()
        mocked_avariant.POS = pos
        mocked_avariant.genotypes = [[1, -1]]
        mocked_avariant.ALT = ["C"]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[0, False]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Alt, Classification.Ref, Outcome.FalseRef

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_aIsRefBIsAlt_returnsFalseAlt(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier()
        mocked_avariant.POS = pos
        mocked_avariant.genotypes = [[0, 0]]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[3]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Ref, Classification.Alt, Outcome.FalseAlt

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_bothAlt_returnsTrueAlt(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier()
        mocked_avariant.POS = pos
        mocked_avariant.genotypes = [[1, 1]]
        mocked_avariant.ALT = ["C"]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[1]]
        mocked_bvariant.ALT = ["C"]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Alt, Classification.Alt, Outcome.TrueAlt

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_bothAltButDifferent_returnsDiffAlt(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier()
        mocked_avariant.POS = pos
        mocked_avariant.genotypes = [[1, 1]]
        mocked_avariant.ALT = ["C"]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[1]]
        mocked_bvariant.ALT = ["A"]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Alt, Classification.Alt, Outcome.DiffAlt

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_bothFailFilter_returnsBothFailFilter(
        self, mocked_avariant, mocked_bvariant
    ):
        pos = 2
        classifier = Classifier(apply_filter=True)
        mocked_avariant.POS = pos
        mocked_avariant.FILTER = "b1"
        mocked_avariant.genotypes = [[0, 0]]
        mocked_bvariant.POS = pos
        mocked_bvariant.FILTER = "f0.90;z"
        mocked_bvariant.genotypes = [[0]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Ref, Classification.Ref, Outcome.BothFailFilter

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_aFailFilter_returnsAFailFilter(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier(apply_filter=True)
        mocked_avariant.POS = pos
        mocked_avariant.FILTER = "b1"
        mocked_avariant.genotypes = [[0, 0]]
        mocked_bvariant.POS = pos
        mocked_bvariant.FILTER = None
        mocked_bvariant.genotypes = [[0, 0]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Ref, Classification.Ref, Outcome.AFailFilter

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_bFailFilter_returnsBFailFilter(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier(apply_filter=True)
        mocked_avariant.POS = pos
        mocked_avariant.FILTER = None
        mocked_avariant.genotypes = [[0, 0]]
        mocked_bvariant.POS = pos
        mocked_bvariant.FILTER = "foo;bar"
        mocked_bvariant.genotypes = [[0, 0]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Ref, Classification.Ref, Outcome.BFailFilter

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_bothHet_returnsBothHet(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier()
        mocked_avariant.POS = pos
        mocked_avariant.genotypes = [[0, 1]]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[0, 1]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Het, Classification.Het, Outcome.Het

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_aIsHet_returnsAHet(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier()
        mocked_avariant.POS = pos
        mocked_avariant.genotypes = [[0, 1]]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[0]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Het, Classification.Ref, Outcome.Het

        assert actual == expected

    @patch("cyvcf2.Variant", autospec=True, create=True)
    @patch("cyvcf2.Variant", autospec=True, create=True)
    def test_bIsHet_returnsBHet(self, mocked_avariant, mocked_bvariant):
        pos = 2
        classifier = Classifier()
        mocked_avariant.POS = pos
        mocked_avariant.genotypes = [[0, 0]]
        mocked_bvariant.POS = pos
        mocked_bvariant.genotypes = [[0, 1]]

        actual = classifier.classify(mocked_avariant, mocked_bvariant)
        expected = Classification.Ref, Classification.Het, Outcome.Het

        assert actual == expected


class TestCalculateCallRate:
    def test_noAltInA_returnsOne(self, dataset: pd.DataFrame):
        df = dataset.query("a != @Classification.Alt")
        calculator = Calculator()

        actual = calculator.call_rate(df, genome_wide=False)
        expected = 1.0

        assert actual == approx(expected)

    def test_allPermutations(self, dataset: pd.DataFrame):
        calculator = Calculator()

        actual = calculator.call_rate(dataset, genome_wide=False)
        expected = 4 / 7

        assert actual == approx(expected)


class TestCalculateGenomeWideCallRate:
    def test_noRefOrAltInA_returnsOne(self, dataset: pd.DataFrame):
        df = dataset.query("a not in [@Classification.Alt, @Classification.Ref]")
        calculator = Calculator()

        actual = calculator.call_rate(df, genome_wide=True)
        expected = 1.0

        assert actual == approx(expected)

    def test_allPermutations(self, dataset: pd.DataFrame):
        calculator = Calculator()

        actual = calculator.call_rate(dataset, genome_wide=True)
        expected = 7 / 13

        assert actual == approx(expected)


class TestCalculateConcordance:
    def test_noAltInA_returnsOne(self, dataset: pd.DataFrame):
        df = dataset.query("a != @Classification.Alt")
        calculator = Calculator()

        actual = calculator.concordance(df, genome_wide=False)
        expected = 1.0

        assert actual == approx(expected)

    def test_allPermutations(self, dataset: pd.DataFrame):
        calculator = Calculator()

        actual = calculator.concordance(dataset, genome_wide=False)
        expected = 1 / 3

        assert actual == approx(expected)


class TestCalculateGenomeWideConcordance:
    def test_noRefOrAltInA_returnsOne(self, dataset: pd.DataFrame):
        df = dataset.query("a not in [@Classification.Alt, @Classification.Ref]")
        calculator = Calculator()

        actual = calculator.concordance(df, genome_wide=True)
        expected = 1.0

        assert actual == approx(expected)

    def test_allPermutations(self, dataset: pd.DataFrame):
        calculator = Calculator()

        actual = calculator.concordance(dataset, genome_wide=True)
        expected = 2 / 5

        assert actual == approx(expected)
