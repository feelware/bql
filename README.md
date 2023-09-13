```
dP                dP 
88                88 
88d888b. .d8888b. 88 
88'  `88 88'  `88 88 
88.  .88 88.  .88 88 
88Y8888' `8888P88 dP 
            88    
            dP    

boolean query language
```

## Description
Simple utility for filtering .csv files based on boolean expressions and picking which columns to keep. Made as a project for my Discrete Math class at UNMSM.

## Usage
### Atomic statements are of the form:
```
<statement> := <field> <operator> '<value>'
<statement> := <negation> <statement>
```
Where `<field>` is one of the fields available in the csv file, `<operator>` is one of the following:
- `==` : equal to
- `!=` : not equal to
- `?=` : matches regex

`<value>` is the string to match and `<negation>` is either `not` or empty.

### Molecular statements are of the form:
```
<statement> := <statement> <boolean operator> <statement>
```
Where `<boolean operator>` is one of the following:
- `and` : ∧
- `or` : ∨
- `then` : →
- `iff` : ↔

You can use parentheses to group statements.
```
<statement> := (<statement>)
```

## Credits
Gareth Rees. [Creating truth table from a logical statement](https://codereview.stackexchange.com/questions/145465/creating-truth-table-from-a-logical-statement). 2016-10-29.