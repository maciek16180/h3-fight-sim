# h3-fight-sim

W tej chwili wyniki są nieaktualne!

Opis plików:

CRTRAITS.TXT - dane o stworkach. Wyczyszczona i lekko zmieniona wersja, w nieco innym formacie niż oryginalny plik z gry.  
combat_sim.ipynb - na razie tu siedzi cały kod bitew, notebook jest wygodny do ekspermentów

misc/ - pierdoły (chociaż stwory.csv jest całkiem przydatny przy grze :D)  
castle_scores/  
 - castle_scores.csv - względne oceny jednostek Zamku na podstawie symulacji  
 - castle_scores_ai_value_based.csv - oceny oparte na AI Value  
 - caste_comparison.csv - porównanie powyższych
  
#####  

Jak czytać wyniki:

castle_scores.csv:  
  Jednostka X walczy z Y. Eksperymentalnie dobieram liczby jednostek (nX i nY) w oddziałach tak, żeby szanse wygranej każdej ze stron były mniej więcej równe. Liczba w wierszu X i kolumnie Y to nX/nY, czyli ile X trzeba, żeby sprać jednego Y.
  
castle_scores_ai_value_based.csv:  
  Liczba w wierszu X i kolumnie Y to Y.aivalue/X.aivalue.
  
castle_comparison.csv:  
  Iloraz pierwszego i drugiego. Usunąłem wyniki bliskie 1 dla lepszej czytelności. Jeśli liczba w wierszu X i kolumnie Y jest mniejsza od 1, to heurystyka AI Value nie docenia X. Jeśli jest większa od 1, to heurystyka przecenia X.
  
#####

Uwagi:

- Symulacje dają w miarę stabilne rezultaty dla dużych oddziałów, dla małych wyniki są dość zachwiane (wina mechaniki, nie kodu). Np. 8 Archaniołów klepie bez problemu 510 Pikinierów, ale 80 Archaniołów i 5100 Pikinierów ma w miarę równe szanse. Ogólnie duże jednostki sprawdzają się znacznie lepiej w małych potyczkach.

- Jednostki Zamku liczyły się łącznie jakąś godzinę. Nie robiłem w zasadzie żadnych optymalizacji, żeby kod był bardziej zrozumiały, ale ostatni "poziom" - szukanie zbalansowanych rozmiarów oddziałów - można łatwo zrównoleglić.

- Nie wszystkie umiejętności potworów są wzięte pod uwagę, ale chyba większość najistotniejszych zrobiłem:
    - duża istota (przy obliczaniu odległości od strzelca)
    - strzelanie
    - brak kontrataku
    - brak kar w walce wręcz / na odległość
    - podwójny atak / strzał
    - odrodzenie Feniksa
    - obniżanie obrony Behemotów
    - podwójne obrażenia Upiornego rycerza
    - wyssanie życia Wampirzego lorda
    - spojrzenie śmierci Wielkiej gorgony
    - nienawiść i podwójne obrażenia żywiołaków
    - strach Błękitnego smoka
    - regeneracja Zjaw i Trolli
    - tarcza ognia Sułtańskich ifrytów
    - kwasowy oddech Rdzawego smoka
    - atak błyskawicą Ptaka gromu
    - postarzanie Upiornego smoka
    - zatrucie Królewskiej wiwerny
    - klątwa Mumii i Czarnych / Upiornych rycerzy (drobna nieścisłość w czasie trwania)
    - osłabienie Smoczej ważki (j.w.)
    
- W walce strzelca ze zwykłą jednostką sprawdzam ile strzałów jest wykonywane z karą za odległość (przy założeniu optymalnych ruchów obu stron, wliczając czekanie - wydaje mi się, że komputer to umie)
