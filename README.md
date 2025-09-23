# projeto_integrador_4
Repositório destinado ao conjunto de atividades desenvolvidas em torno do Projeto Integrador no 4º semestre do curso de ADS. O foco será uma aplicação em torno de IOT.

## Estrutura do Projeto
bus-iot-monitoring/
│
├── README.md # Descrição do projeto, instruções, requisitos
├── LICENSE # Licença do projeto
├── requirements.txt # Dependências Python (ML, API, etc.)
│
├── hardware/ # Código embarcado e docs de hardware
│ ├── ESP32_S3/
│ │ ├── main.ino # Código principal do ESP32-S3
│ │ ├── camera.ino # Captura de imagens (OV2640)
│ │ └── gps_gprs.ino # Envio de coordenadas via GPRS
│ └── docs/ # Esquemas de ligação e datasheets
│
├── server/ # Servidor em nuvem (API + ML + DB)
│ ├── api/ # Endpoints HTTP
│ ├── ml/ # Modelos de Machine Learning
│ ├── db/ # Scripts do banco de dados
│ └── config.py # Configurações gerais
│
├── client/ # Front-end (Totem/Dashboard)
│ ├── dashboard/
│ │ ├── app.py # Dashboard (Flask/Streamlit)
│ │ └── templates/ # HTML/CSS/JS
│ └── config.py
│
├── data/ # Dados de exemplo e logs
├── tests/ # Testes unitários e integração
└── docs/ # Documentação e diagramas
