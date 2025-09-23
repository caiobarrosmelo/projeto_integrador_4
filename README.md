# projeto_integrador_4
Repositório destinado ao conjunto de atividades desenvolvidas em torno do Projeto Integrador no 4º semestre do curso de ADS. O foco será uma aplicação em torno de IoT.

# Bus IoT Monitoring

Sistema de monitoramento IoT para coleta de dados de dispositivos ESP32, processamento na nuvem e visualização em dashboard. O projeto inclui integração com Machine Learning para previsão de ocupação e análise de dados.

---

## Estrutura do Projeto

```text
projeto_integrador_4/
│
├── README.md                       # Este arquivo
├── LICENSE                         # Licença do projeto
├── requirements.txt                # Bibliotecas Python necessárias (ML, API, etc.)
│
├── hardware/                       # Código e componentes do dispositivo ESP32
│   ├── ESP32_S3/
│   │   ├── main.ino                # Código principal para ESP32S3
│   │   ├── camera.ino              # Captura de imagens
│   │   └── gps_gprs.ino            # Envio de coordenadas via GPRS
│   └── docs/                       # Esquemas de ligação, datasheets
│
├── server/                         # Código do servidor na nuvem
│   ├── api/                        # Endpoints HTTP para recebimento de dados
│   │   ├── receive_location.py
│   │   ├── receive_image.py
│   │   └── utils.py
│   ├── ml/                         # Modelos de Machine Learning
│   │   ├── yolov5/                 # Código e pesos do YOLO
│   │   └── occupancy_predictor.py
│   ├── db/                         # Scripts de criação e seed do banco de dados
│   │   ├── create_tables.sql
│   │   └── seed_data.sql
│   └── config.py                   # Configurações gerais (DB, API keys)
│
├── client/                         # Front-end (Totem/Display)
│   ├── app/                        # Páginas e layouts da aplicação
│   ├── components/                 # Componentes reutilizáveis
│   └── lib/                        # Utilitários e configurações
│
├── data/                           # Dados de exemplo e logs
│   ├── sample_images/
│   ├── gps_logs.csv
│   └── prediction_logs.csv
│
├── tests/                          # Testes unitários e de integração
│   ├── test_esp32.py
│   ├── test_server.py
│   └── test_ml.py
│
└── docs/                           # Documentação adicional
    ├── diagram_ER.png              # Modelo ER do banco
    ├── flowchart.png               # Fluxo de coleta → processamento → dashboard
    └── setup_guide.md
````

---
