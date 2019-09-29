# loopterm
A CLI for SchoolLoop

## Install
Install dependencies.
```
pip install -r requirements.txt
```
Clone the repository.
```
https://github.com/juniorRubyist/loopterm.git
```

## Usage
### Login – Do this first.
```sh
python3 loopterm login
```
Follow the prompts to save your login information.
The "subdomain" is `*.schoolloop.com`. Nothing else.

### Grades
```sh
python3 loopterm grades [--period/-p period]
```
The optional `--period`/`-p` option allows you to specify the period you want.

### Progress Report
```sh
python3 loopterm report PERIOD [--zeros/-0]
```
`PERIOD` is the period you want data for.
The optional `--zeros`/`-0` flag will show only zeros.

### Zeros Report
```sh
python3 loopterm zeros PERIOD
```
`PERIOD` is the period you want data for.

Alias for `report PERIOD --zeros`.
