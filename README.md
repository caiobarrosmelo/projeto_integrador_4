# projeto_integrador_4
Repositório destinado ao conjunto de atividades desenvolvidas em torno do Projeto Integrador no 4º semestre do curso de ADS. O foco será uma aplicação em torno de IOT.


bus-iot-monitoring/
│
├── README.md                  # Descrição do projeto, instruções, requisitos
├── LICENSE                    # Licença do projeto
├── requirements.txt           # Bibliotecas Python necessárias (para ML, API, etc.)
│
├── hardware/                  # Componentes e código do dispositivo ESP32
│   ├── ESP32_S3/              
│   │   ├── main.ino           # Código principal para ESP32S3
│   │   ├── camera.ino         # Código de captura de imagens
│   │   └── gps_gprs.ino       # Código de envio de coordenadas via GPRS
│   └── docs/                  # Esquemas de ligação, datasheets
│
├── server/                    # Código do servidor na nuvem
│   ├── api/                   # Endpoints HTTP para receber dados
│   │   ├── receive_location.py
│   │   ├── receive_image.py
│   │   └── utils.py
│   ├── ml/                    # Modelos de Machine Learning
│   │   ├── yolov5/             # Código e pesos do YOLO
│   │   └── occupancy_predictor.py
│   ├── db/                    # Scripts de criação do banco de dados
│   │   ├── create_tables.sql
│   │   └── seed_data.sql
│   └── config.py              # Configurações gerais (DB, API keys)
│
├── client/                    # Código do front-end (Totem/Display)
│   ├── dashboard/             
│   │   ├── app.py             # Flask/Streamlit dashboard
│   │   └── templates/         # HTML/CSS/JS se necessário
│   └── config.py
│
├── data/                      # Dados de exemplo e logs (para teste)
│   ├── sample_images/
│   ├── gps_logs.csv
│   └── prediction_logs.csv
│
├── tests/                     # Testes unitários e integração
│   ├── test_esp32.py
│   ├── test_server.py
│   └── test_ml.py
│
└── docs/                      # Documentação adicional
    ├── diagram_ER.png          # Modelo ER do banco de dados
    ├── flowchart.png           # Fluxo de coleta → processamento → display
    └── setup_guide.md