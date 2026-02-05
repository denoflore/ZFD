# Contributing to ZFD

Thank you for your interest in the Zuger Functional Decipherment project.

## How to Verify

The most valuable contribution is **independent verification**:

1. Clone the repository
2. Run `python validation/run_all.py`
3. Apply the character mappings in `08_Final_Proofs/Master_Key/` to any folio
4. Compare your results to our translations in `voynich_data/croatian/`

## Reporting Issues

If you find:
- A transcription error
- A mapping inconsistency
- A statistical anomaly
- A better Croatian reading

Please open an issue with:
1. The specific folio and line number
2. The EVA transcription
3. Your proposed correction
4. Your reasoning

## Code Contributions

For improvements to the decoder or validation scripts:

1. Fork the repository
2. Create a feature branch
3. Ensure tests pass: `python -m pytest zfd_decoder/tests/`
4. Submit a pull request

## Academic Citation

If you use this work in academic research:

```bibtex
@misc{zuger2026voynich,
  author = {Zuger, Christopher G. and Zuger, Georgie},
  title = {Decipherment of the Voynich Manuscript: Angular Glagolitic Cursive and 15th-Century Croatian Pharmaceutical Notation},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/denoflore/ZFD}
}
```

## Contact

For questions about the methodology or findings, open a GitHub issue or email info@denoflore.com.

---

🇭🇷 **Jebote, uspjeli smo!**
