# Test di mersenne

I test di **mersenne** sono divisi in tre cartelle:
1. `unit`: questa cartella contiene i test di unità di `mersenne`. I moduli testati in ciascun file non operano sul database e non accedono a gare passate.
2. `integration`: questa cartella contiene test di integrazione tra più unità di `mersenne`. I test possono operare sul database e utilizzare le gare salvate in `data`, ma non interrogano mai un browser.
3. `browser`: questa cartella contiene test end to end. I test possono operare sul database e utilizzare le gare salvate in `data`, e interrogano sempre un browser.
