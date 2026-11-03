# Sony's GPL and LGPL sources for our two model groups

The source Sony published for the BRAVIA EX725 and HX855 groups (2010 to 2012): both Linux kernels, Sony's patched userland, the cross compiler and the other packages of our groups' pages.
Sony removed them from its site; the Internet Archive collection [sony-gpl-source](https://archive.org/details/sony-gpl-source) kept them, and [uyjulian](https://github.com/uyjulian) found them there ([issue #27](https://github.com/danielcamposramos/sony-bravia-linux/issues/27)).

- `common/<folder>/<file>`: Sony's own layout. Each folder name is the file's MD5 in base64, with `/` written as `_`, so a file shared by many models is stored once.
- `SHA256SUMS` and `MD5SUMS`: all 30 files, checked against their folder names and against the hashes the Internet Archive publishes.
- Which group each file belongs to, how sure we are, and what the patched packages hold: [docs/research/gpl-sources-mirror.md](../docs/research/gpl-sources-mirror.md).
- The two kernels, surveyed: [docs/research/gpl-kernels-2623-survey.md](../docs/research/gpl-kernels-2623-survey.md).

These files are Sony's, under the GPL and LGPL licences each package carries; their licences are what let us keep them here.
They are the one exception to this repository's rule of hosting no Sony-distributed material.
