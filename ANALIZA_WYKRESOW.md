# Analiza i ulepszenia wykresów

## Problemy z obecnymi wykresami

1. **Zbyt mało punktów danych** - wykresy pokazują tylko średnie, więc jeśli dla danego n1 jest tylko jeden test, nie widać trendu
2. **Losowe dane z różnych testów** - testy pochodzą z różnych plików, więc nie ma systematycznego pokrycia parametrów
3. **Brak wizualizacji wszystkich punktów** - widzimy tylko linie średnich, nie widzimy rozproszenia danych
4. **Podwykresy mogą być puste lub mieć tylko 1-2 punkty** - nie wszystkie kombinacje (n2, k) mają wystarczająco danych

## Nowe ulepszone wykresy

Utworzyłem `generate_plots_improved.py` z następującymi ulepszeniami:

### 1. **time_vs_parameters_scatter.png**
   - **Scatter plots** pokazujące wszystkie punkty danych (nie tylko średnie)
   - **Box plots** pokazujące rozkład czasu dla różnych wartości parametrów
   - Widać wszystkie testy, nie tylko uśrednione wartości

### 2. **heatmap_time_*.png**
   - **Heatmapy** pokazujące średni czas dla różnych kombinacji n1 × n2
   - Białe komórki = brak danych
   - Kolorowe komórki = średni czas (im ciemniejszy, tym dłuższy czas)
   - Wartości liczbowe w komórkach

### 3. **aggregated_trends.png**
   - **Trendy z odchyleniem standardowym** - pokazuje nie tylko średnie, ale też zmienność
   - **Error bars** pokazujące rozrzut danych
   - Wszystkie dostępne dane są uśredniane, nie tylko wybrane scenariusze

### 4. **size_complexity.png**
   - **Złożoność względem rozmiaru problemu** (n1 × n2 × k)
   - Pokazuje jak czas rośnie z rozmiarem problemu
   - Trend lines pokazujące przybliżoną złożoność

## Jak używać

```bash
# Wygeneruj ulepszone wykresy
python3.13 generate_plots_improved.py

# Lub użyj obu wersji
python3.13 generate_plots.py          # Oryginalne wykresy
python3.13 generate_plots_improved.py # Ulepszone wykresy
```

## Co pokazują nowe wykresy

### Scatter plots
- **Wszystkie punkty danych** - widzisz każdy test osobno
- **Rozproszenie** - widać czy dane są skupione czy rozproszone
- **Outliery** - łatwo zidentyfikować nietypowe przypadki

### Box plots
- **Rozkład danych** - mediana, kwartyle, outliery
- **Porównanie** - łatwo porównać rozkłady dla różnych wartości parametrów
- **Zmienność** - widać jak bardzo różnią się czasy dla tego samego parametru

### Heatmapy
- **Pełny obraz** - wszystkie kombinacje n1 × n2 na jednym wykresie
- **Brakujące dane** - białe komórki pokazują gdzie brakuje testów
- **Wzorce** - łatwo zobaczyć które kombinacje są najtrudniejsze

### Trendy z error bars
- **Niepewność** - error bars pokazują jak bardzo różnią się wyniki
- **Trendy** - widać ogólny kierunek zmian
- **Wiarygodność** - duże error bars = duża zmienność, małe = stabilne wyniki

## Rekomendacje

1. **Użyj obu wersji** - oryginalne pokazują szczegóły dla wybranych scenariuszy, ulepszone pokazują pełny obraz
2. **Dla sprawozdania** - użyj ulepszonych wykresów, są bardziej czytelne
3. **Dla analizy** - użyj scatter plots i box plots, pokazują więcej informacji

