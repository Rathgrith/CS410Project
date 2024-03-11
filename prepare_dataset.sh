#!/bin/bash

# Ensure Kaggle API is installed
if ! command -v kaggle &> /dev/null
then
    echo "Kaggle CLI not found. Installing..."
    pip install kaggle
fi
# if unzip is not installed
if ! command -v unzip &> /dev/null
then
    echo "unzip not found. Installing..."
    sudo apt-get install unzip
fi
# Set up Kaggle API key
# Make sure to replace "YOUR_API_KEY" with your actual Kaggle API key
# You can find your API key at https://www.kaggle.com/account
# export KAGGLE_USERNAME=YOUR_API_KEY
# export KAGGLE_KEY=YOUR_API_KEY

# Download dataset
kaggle datasets download -d Cornell-University/arxiv

# Optionally, you can unzip the downloaded dataset
echo "Unzipping dataset..."
unzip arxiv.zip

