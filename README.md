# CBRF DATA RECEIVER

## Description

This service retrieves currency exchange rate data by querying the REST API 
of the Central Bank (CBR), parses the data, and stores it in a PostgreSQL database.

## Локальная установка

1. Fill in all the necessary fields in the configuration file

`/cbr_data_receiver/config/local/access.yaml`

2. Navigate to the application directory and enter the command

`make install`

3. Apply migrations to an existing database with the following command

`make migrations`

4. Run tests with the command

`make tests`

5. Start the application with the command

`make start`
