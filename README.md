# Serverless Data Pipeline with AWS CDK, Lake Formation, and Glue

Este proyecto implementa un pipeline de datos completo y sin servidor en AWS, construido utilizando el AWS Cloud Development Kit (CDK) con Python. El pipeline extrae datos de una API pública, los almacena en un data lake gobernado en S3, los cataloga con AWS Glue y los hace disponibles para consulta a través de Amazon Athena, todo bajo el gobierno de permisos de AWS Lake Formation.

---

## Arquitectura

El pipeline sigue una arquitectura serverless moderna para la ingesta y procesamiento de datos en AWS.



---

## Stack Tecnológico

* **Infraestructura como Código:** AWS CDK (Python)
* **Almacenamiento:** Amazon S3 (en formato Parquet)
* **Procesamiento/ETL:** AWS Lambda con AWS Data Wrangler
* **Catálogo de Datos:** AWS Glue (Base de Datos y Crawler)
* **Gobierno y Seguridad:** AWS Lake Formation
* **Consulta y Análisis:** Amazon Athena

---

## Instrucciones de Despliegue

### Prerrequisitos
* [cite_start]AWS CLI configurado con credenciales. [cite: 11]
* [cite_start]AWS CDK v2 instalado. [cite: 12]
* [cite_start]Python 3.10+ y Node.js. [cite: 13, 14]

### Pasos para el Despliegue

1.  **Clonar el Repositorio**
    ```bash
    git clone https://github.com/jufevalencia/aws-cdk-pipeline.git
    cd aws-cdk-pipeline
    ```

2.  **Configurar el Entorno Virtual**
    ```bash
    # Crear y activar el entorno virtual
    python3 -m venv .venv
    source .venv/bin/activate

    # Instalar las dependencias de Python
    pip install -r requirements.txt
    ```

3.  **Bootstrap de CDK (si es necesario)**
    Si es la primera vez que usas CDK en esta cuenta/región, ejecuta:
    ```bash
    cdk bootstrap
    ```

4.  **Desplegar los Stacks**
    Este comando desplegará toda la infraestructura (Data Lake y ETL).
    ```bash
    cdk deploy --all
    ```
    CDK te mostrará los cambios y pedirá confirmación. Escribe `y` para aprobar.

---

## Validación y Pruebas

Una vez desplegado, puedes validar el pipeline de la siguiente manera:

1.  **Invocar la Función Lambda:**
    * Ve a la consola de AWS -> Lambda.
    * Busca la función `DataExtractorLambda` y ejecútala con un evento de prueba.
    * [cite_start]Verifica en tu bucket de S3 que se ha creado un nuevo archivo Parquet en la ruta `raw/users/year=.../`. [cite: 85]

2.  **Ejecutar el Crawler de Glue:**
    * Ve a la consola de AWS -> Glue.
    * Busca el crawler `DataLakeCrawler`, selecciónalo y ejecútalo.
    * [cite_start]Al finalizar, una nueva tabla llamada `users` debería aparecer en la base de datos `serverless_data_lake_db`. [cite: 86]

3.  **Consultar con Athena:**
    * Ve a la consola de AWS -> Athena.
    * Asegúrate de que el Data Source sea `AwsDataCatalog` y la base de datos sea `serverless_data_lake_db`.
    * [cite_start]Ejecuta la siguiente consulta para ver los datos: [cite: 87]
      ```sql
      SELECT name, email, phone FROM users LIMIT 10;
      ```

4.  **Validar Permisos de Lake Formation:**
    * Para demostrar la seguridad a nivel de columna, necesitarías un rol de IAM (que no sea el de administrador) al que solo le hayas dado permiso `SELECT` a columnas específicas (ej. `name`, `email`) a través de Lake Formation.
    * [cite_start]Al asumir ese rol, la consulta anterior funcionaría, pero la siguiente consulta fallaría con un error de permisos: [cite: 88]
      ```sql
      SELECT * FROM users LIMIT 10;
      ```
