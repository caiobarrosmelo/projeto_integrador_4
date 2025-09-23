# projeto_integrador_4
Repositório destinado ao conjunto de atividades desenvolvidas em torno do Projeto Integrador no 4º semestre do curso de ADS. O foco será uma aplicação em torno de IOT.

```markdown
# Bus IoT Monitoring

Sistema de monitoramento IoT para coleta de dados de dispositivos ESP32, processamento na nuvem e visualização em dashboard. O projeto inclui integração com Machine Learning para previsão de ocupação e análise de dados.

---

## Estrutura do Projeto

``` text

bus-iot-monitoring/
│
├── README.md                  # Este arquivo
├── LICENSE                    # Licença do projeto
├── requirements.txt           # Bibliotecas Python necessárias (ML, API, etc.)
│
├── hardware/                  # Código e componentes do dispositivo ESP32
│   ├── ESP32\_S3/
│   │   ├── main.ino           # Código principal para ESP32S3
│   │   ├── camera.ino         # Captura de imagens
│   │   └── gps\_gprs.ino       # Envio de coordenadas via GPRS
│   └── docs/                  # Esquemas de ligação, datasheets
│
├── server/                    # Código do servidor na nuvem
│   ├── api/                   # Endpoints HTTP para recebimento de dados
│   │   ├── receive\_location.py
│   │   ├── receive\_image.py
│   │   └── utils.py
│   ├── ml/                    # Modelos de Machine Learning
│   │   ├── yolov5/             # Código e pesos do YOLO
│   │   └── occupancy\_predictor.py
│   ├── db/                    # Scripts de criação e seed do banco de dados
│   │   ├── create\_tables.sql
│   │   └── seed\_data.sql
│   └── config.py              # Configurações gerais (DB, API keys)
│
├── client/                    # Front-end (Totem/Display)
│   ├── dashboard/
│   │   ├── app.py             # Dashboard Flask/Streamlit
│   │   └── templates/         # HTML/CSS/JS
│   └── config.py
│
├── data/                      # Dados de exemplo e logs
│   ├── sample\_images/
│   ├── gps\_logs.csv
│   └── prediction\_logs.csv
│
├── tests/                     # Testes unitários e de integração
│   ├── test\_esp32.py
│   ├── test\_server.py
│   └── test\_ml.py
│
└── docs/                      # Documentação adicional
├── diagram\_ER.png          # Modelo ER do banco
├── flowchart.png           # Fluxo de coleta → processamento → dashboard
└── setup\_guide.md

```

---

## Pré-requisitos

- Python 3.10+
- PostgreSQL 15+
- Bibliotecas listadas em `requirements.txt`
- Dispositivo ESP32S3 compatível com código fornecido

---

## Instalação e Execução

1. Clone o repositório:
```bash
git clone [https://github.com/caiobarrosmelo/projeto_integrador_4.git]
cd bus-iot-monitoring
````

2. Instale dependências Python:

```bash
pip install -r requirements.txt
```

3. Configure o banco de dados PostgreSQL:

```bash
createdb bus_iot_monitoring
psql -d bus_iot_monitoring -f server/db/create_tables.sql
psql -d bus_iot_monitoring -f server/db/seed_data.sql
```

4. Execute o servidor:

```bash
python server/api/receive_location.py
python server/api/receive_image.py
```

5. Inicie o dashboard:

```bash
python client/dashboard/app.py
```

---

## Licença

*Haverá?*
