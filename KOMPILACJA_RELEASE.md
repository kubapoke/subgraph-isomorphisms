# Kompilacja w trybie Release - krok po kroku

## Metoda 1: Rekonfiguracja istniejącego build (ZALECANE)

### Krok 1: Przejdź do katalogu build
```bash
cd build
```

### Krok 2: Skonfiguruj CMake w trybie Release
```bash
cmake -DCMAKE_BUILD_TYPE=Release ..
```

### Krok 3: Skompiluj
```bash
cmake --build . --config Release
```

Lub jeśli używasz make:
```bash
make
```

### Krok 4: Sprawdź wynik
```bash
# Windows
dir subgraph-isomorphism.exe

# Lub sprawdź rozmiar - Release powinien być większy (zoptymalizowany)
```

---

## Metoda 2: Nowy folder build-release (czystsze rozwiązanie)

### Krok 1: Utwórz nowy folder
```bash
mkdir build-release
cd build-release
```

### Krok 2: Skonfiguruj CMake w trybie Release
```bash
cmake -DCMAKE_BUILD_TYPE=Release ..
```

### Krok 3: Skompiluj
```bash
cmake --build . --config Release
```

Lub:
```bash
make
```

### Krok 4: Sprawdź wynik
```bash
# Windows
dir subgraph-isomorphism.exe
```

---

## Metoda 3: Multi-config (Visual Studio)

Jeśli używasz Visual Studio generator:

### Krok 1: Skonfiguruj z generatorem Visual Studio
```bash
cd build
cmake -G "Visual Studio 17 2022" -DCMAKE_BUILD_TYPE=Release ..
```

### Krok 2: Skompiluj w trybie Release
```bash
cmake --build . --config Release
```

---

## Różnice między Debug a Release

| Aspekt | Debug | Release |
|--------|-------|---------|
| **Optymalizacja** | Brak (-O0) | Pełna (-O3) |
| **Debug info** | Tak (-g) | Nie |
| **Rozmiar exe** | Mniejszy | Większy (zoptymalizowany) |
| **Szybkość** | Wolniejszy | Szybszy |
| **Asserty** | Działają | Często wyłączone |

## Sprawdzenie czy to Release

### Windows (PowerShell):
```powershell
# Sprawdź czy exe istnieje
Test-Path build\subgraph-isomorphism.exe

# Sprawdź rozmiar (Release jest zwykle większy)
(Get-Item build\subgraph-isomorphism.exe).Length
```

### Sprawdź flagi kompilacji:
```bash
# W build/CMakeCache.txt szukaj:
CMAKE_CXX_FLAGS_RELEASE
```

---

## Pełna komenda (wszystko naraz)

Z głównego katalogu projektu:

```bash
# Windows (cmd)
cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && cmake --build . --config Release

# Windows (PowerShell)
cd build; cmake -DCMAKE_BUILD_TYPE=Release ..; cmake --build . --config Release

# Linux/Mac
cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make
```

---

## Uwagi

1. **Jeśli masz już skonfigurowany build w trybie Debug:**
   - Najlepiej wyczyścić folder `build` lub użyć nowego folderu `build-release`
   - Lub po prostu uruchomić `cmake -DCMAKE_BUILD_TYPE=Release ..` w folderze build

2. **Domyślny tryb:**
   - Jeśli nie podasz `CMAKE_BUILD_TYPE`, CMake używa trybu bez optymalizacji
   - Zawsze podawaj `-DCMAKE_BUILD_TYPE=Release` dla wydajności

3. **Sprawdzenie aktualnego trybu:**
   - Otwórz `build/CMakeCache.txt`
   - Szukaj linii: `CMAKE_BUILD_TYPE:STRING=Release` (lub Debug)

---

## Troubleshooting

### Problem: "CMake Error: No CMAKE_BUILD_TYPE specified"
**Rozwiązanie:** Dodaj `-DCMAKE_BUILD_TYPE=Release` przy konfiguracji

### Problem: Exe nie jest szybszy
**Rozwiązanie:** 
- Sprawdź czy faktycznie skompilowałeś w Release
- Wyczyść build: `rm -rf build/*` (Linux) lub usuń zawartość build (Windows)
- Skonfiguruj ponownie z `-DCMAKE_BUILD_TYPE=Release`

### Problem: Chcę mieć oba (Debug i Release)
**Rozwiązanie:** Użyj dwóch folderów:
- `build-debug/` - dla Debug
- `build-release/` - dla Release

