from pathlib import Path

from karzoun_x.datasets import load_labeled_channels


def test_load_labeled_channels(tmp_path: Path) -> None:
    source = tmp_path / "labels.csv"
    source.write_text(
        "chan_id,spacecraft,anomaly_sequences,class,num_values\n"
        'P-1,SMAP,"[[10, 20], [30, 35]]","[contextual, point]",100\n',
        encoding="utf-8",
    )

    channels = load_labeled_channels(source)

    assert len(channels) == 1
    assert channels[0].channel_id == "P-1"
    assert channels[0].spacecraft == "SMAP"
    assert channels[0].anomaly_sequences == ((10, 20), (30, 35))
    assert channels[0].num_values == 100
