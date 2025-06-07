# graphcat.py

Simple script to generate graphs and charts on hashcat potfile and ntds.

## Table of Content

- [graphcat.py](#graphcatpy)
  - [Table of Content](#table-of-content)
  - [Install](#install)
  - [Helper](#helper)
  - [Usage](#usage)
  - [Format](#formats)
  - [Charts example](#charts-example)

## Install

### Prerequisite
```text
apt install python3-venv
```

### Installation
```text
git clone https://github.com/WodenSec/graphcat-ng
cd graphcat-ng
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

## Helper

```text
$ graphcat.py -h
usage: graphcat.py [-h] -p hashcat.potfile -H hashfile.txt [-f FORMAT] [-e] [-o OUTPUT_DIR] [-d]

Password Cracking Graph Reporting

options:
  -h, --help            show this help message and exit
  -p hashcat.potfile, --potfile hashcat.potfile
                        Hashcat potfile
  -H hashfile.txt, --hashfile hashfile.txt
                        File containing hashes (one per line)
  -f FORMAT, --format FORMAT
                        hashfile format (default 3): 1 for hash; 2 for username:hash; 3 for secretsdump (username:uid:lm:ntlm)
  -e, --export-charts   Output also charts in png
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory
  -d, --debug           Turn DEBUG output ON
```

## Usage

Graphcat just needs a potfile with `-p/--potfile` (hashcat potfile) and a hashfile with `-H/--hashfile`. The hashfile should be in a specific format from the [3 availables formats](#formats) with `-f/--format` flag. Default is **Secretsdump**.

The tool will generate a report with multiple password cracking charts. You can get charts in png with the `-export-charts` flag.

```text
$ graphcat.py -H entreprise.local.ntds -p hashcat.pot
[-] Parsing potfile
[-] 95 entries in potfile
[-] Parsing hashfile
[-] 923 entries in hashfile
[-] Generating graphs...
Results directory: ./results_1723406377
[-] Generating report...
```

### Formats

1: Only Hash

```text
aad3b435b51404eeaad3b435b51404ee
aad3b435b51404eeaad3b435b51404ee
aad3b435b51404eeaad3b435b51404ee
```

2: Username + Hash

```text
test1:aad3b435b51404eeaad3b435b51404ee
test2:aad3b435b51404eeaad3b435b51404ee
test3:aad3b435b51404eeaad3b435b51404ee
```

3: Secretsdump

```text
waza.local\test1:4268:aad3b435b51404eeaad3b435b51404ee:aad3b435b51404eeaad3b435b51404ee:::
waza.local\test2:4269:aad3b435b51404eeaad3b435b51404ee:aad3b435b51404eeaad3b435b51404ee:::
waza.local\test3:4270:aad3b435b51404eeaad3b435b51404ee:aad3b435b51404eeaad3b435b51404ee:::
```

If a hash occurs more than once in the hash file, it will be counted that many times.

Moreover, if you submit secretsdump with password history (`-history` in secretsdump command), it will analyze similarity in password history

## Charts example

<img title="Cracked" src="./assets/cracked.png">
<img title="Format repartition" src="./assets/format.png">
<img title="Length repartition" src="./assets/length.png">
<img title="Top10 most cracked" src="./assets/most.png">
<img title="Top10 basewords" src="./assets/basewords.png">
<img title="Similarity in password history" src="./assets/history.png">
