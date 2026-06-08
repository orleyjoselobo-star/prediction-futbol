# Predicción de Fútbol ⚽

Un modelo predictivo de partidos de fútbol que utiliza machine learning para predecir resultados de partidas de las principales ligas del mundo, la liga colombiana y la Copa del Mundo 2026.

## Características

- 🤖 **Predicciones inteligentes**: Modelos ML entrenados con datos históricos
- 🌍 **Cobertura global**: Liga Premier (Inglaterra), La Liga (España), Serie A (Italia), Bundesliga (Alemania), Ligue 1 (Francia), MLS (USA)
- 🇨🇴 **Liga Colombiana**: Predicciones para la Categoría A
- 🏆 **Copa del Mundo 2026**: Análisis y predicciones del torneo
- 📊 **Estadísticas**: Rendimiento histórico de equipos y análisis de cuotas
- 🤖 **Bot Telegram**: Interfaz interactiva para consultar predicciones
- ☁️ **Google Cloud Run**: Deployado en infraestructura cloud escalable

## Requisitos

- Python 3.9+
- Cuenta de Google Cloud Project
- Bot de Telegram configurado
- API keys para las casas de apuestas (opcional)

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/orleyjoselobo-star/prediction-futbol.git
cd prediction-futbol
```

2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno en `.env`:
```
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
GOOGLE_CLOUD_PROJECT=your_project_id
FIREBASE_CREDENTIALS=path/to/credentials.json
```

## Estructura del Proyecto

```
prediction-futbol/
├── src/
│   ├── models/           # Modelos de machine learning
│   ├── data/             # Scripts para obtener y procesar datos
│   ├── api/              # Integraciones con APIs externas
│   ├── telegram_bot/     # Bot de Telegram
│   ├── cloud_run/        # Configuración para Cloud Run
│   └── utils/            # Funciones auxiliares
├── data/
│   ├── raw/              # Datos sin procesar
│   └── processed/        # Datos procesados
├── notebooks/            # Jupyter notebooks para análisis
├── tests/                # Tests unitarios
├── requirements.txt      # Dependencias Python
├── .env.example          # Plantilla de variables de entorno
├── Dockerfile            # Configuración para Cloud Run
└── README.md             # Este archivo
```

## Uso del Bot Telegram

1. Inicia el bot:
```bash
python src/telegram_bot/main.py
```

2. En Telegram, presiona `/start` para ver los partidos del día

3. Selecciona un partido para ver:
   - Predicción del resultado
   - Probabilidades por resultado
   - Estadísticas clave de los equipos
   - Recomendaciones de apuestas

## Modelos Utilizados

- **XGBoost**: Modelo principal para predicción de resultados
- **LightGBM**: Modelo complementario para validación cruzada
- **Análisis de Series Temporales**: Tendencias históricas de equipos
- **Features de apuestas**: Cuotas de casas de apuestas como predictores

## Fuentes de Datos

- API de fútbol: [Football-Data.org](https://www.football-data.org/)
- Datos históricos: Kaggle Datasets
- Cuotas de apuestas: Integraciones con BET365, Bwin, Betano
- Datos en vivo: Espn, FlashScore

## Deployment en Google Cloud Run

Para desplegar en Cloud Run:

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/prediction-futbol
gcloud run deploy prediction-futbol \
  --image gcr.io/PROJECT_ID/prediction-futbol \
  --platform managed \
  --region us-central1
```

## Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT - ver LICENSE para más detalles.

## Autor

**Orely Jose Lobo** - [@orleyjoselobo-star](https://github.com/orleyjoselobo-star)

## Disclaimer

⚠️ **Importante**: Las predicciones son solo estimaciones basadas en datos históricos. No garantizamos exactitud y no es recomendación financiera. Apuesta responsablemente.

---

¿Preguntas? Abre un [issue](https://github.com/orleyjoselobo-star/prediction-futbol/issues) o contacta al autor.