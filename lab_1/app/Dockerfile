FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Copiază fișierul aplicației
COPY app.py .

# Instalează dependențele Python
RUN pip install --no-cache-dir \
    streamlit \
    pandas \
    matplotlib \
    plotly \
    pdfkit \
    ydata-profiling \
    seaborn

EXPOSE 8501

ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD ["streamlit", "run", "app.py"]
