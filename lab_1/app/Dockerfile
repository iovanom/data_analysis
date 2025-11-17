FROM debian:bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

COPY app.py .

RUN pip3 install --no-cache-dir \
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
