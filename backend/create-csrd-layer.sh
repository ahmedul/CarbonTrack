#!/bin/bash
# Create Lambda Layer for CSRD module dependencies
# This layer contains ReportLab and other CSRD-specific dependencies

set -e

echo "🎨 Creating CSRD Lambda Layer"
echo "=============================="
echo ""

LAYER_NAME="carbontrack-csrd-layer"
REGION="eu-central-1"
LAYER_DIR="lambda-layer-csrd"
PYTHON_VERSION="python3.10"

echo "📦 Step 1: Cleaning previous layer build..."
rm -rf $LAYER_DIR
mkdir -p $LAYER_DIR/python

echo ""
echo "📋 Step 2: Creating CSRD dependencies list..."
cat > /tmp/csrd-requirements.txt << 'EOF'
# CSRD-specific dependencies (PDF generation, XBRL, etc.)
reportlab==4.0.7
structlog==23.2.0
lxml==5.1.0
openpyxl==3.1.2

# Additional utilities for CSRD
orjson==3.9.10
EOF

echo ""
echo "📥 Step 3: Installing CSRD dependencies..."
pip install -r /tmp/csrd-requirements.txt -t $LAYER_DIR/python/ --quiet --platform manylinux2014_x86_64 --only-binary=:all:

echo ""
echo "🗜️ Step 4: Creating layer ZIP..."
cd $LAYER_DIR
zip -r ../csrd-layer.zip . -q
cd ..

SIZE=$(du -h csrd-layer.zip | cut -f1)
echo "   Layer size: $SIZE"

echo ""
echo "☁️ Step 5: Publishing Lambda Layer..."
LAYER_VERSION=$(aws lambda publish-layer-version \
    --layer-name $LAYER_NAME \
    --description "CSRD module dependencies (ReportLab, XBRL, etc.)" \
    --zip-file fileb://csrd-layer.zip \
    --compatible-runtimes $PYTHON_VERSION \
    --region $REGION \
    --query 'Version' \
    --output text)

echo "   Layer Version: $LAYER_VERSION"

echo ""
echo "🔗 Step 6: Getting Layer ARN..."
LAYER_ARN=$(aws lambda get-layer-version \
    --layer-name $LAYER_NAME \
    --version-number $LAYER_VERSION \
    --region $REGION \
    --query 'LayerVersionArn' \
    --output text)

echo "   Layer ARN: $LAYER_ARN"

echo ""
echo "✅ CSRD Lambda Layer Created!"
echo ""
echo "📊 Layer Details:"
echo "   Name: $LAYER_NAME"
echo "   Version: $LAYER_VERSION"
echo "   Size: $SIZE"
echo "   ARN: $LAYER_ARN"
echo ""
echo "🔧 Next step: Update Lambda function to use this layer:"
echo "   aws lambda update-function-configuration \\"
echo "     --function-name carbontrack-api \\"
echo "     --layers $LAYER_ARN \\"
echo "     --region $REGION"
echo ""

# Save ARN for next step
echo "$LAYER_ARN" > csrd-layer-arn.txt
echo "💾 Layer ARN saved to csrd-layer-arn.txt"
