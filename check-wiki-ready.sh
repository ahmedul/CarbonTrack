#!/bin/bash
# Quick test to check if wiki is ready
echo "🔍 Testing GitHub wiki availability..."
cd /tmp
rm -rf CarbonTrack.wiki 2>/dev/null
if git clone https://github.com/ahmedul/CarbonTrack.wiki.git 2>/dev/null; then
    echo "✅ Wiki repository is ready!"
    rm -rf CarbonTrack.wiki
    exit 0
else
    echo "❌ Wiki repository not ready yet."
    echo "Please complete the setup steps in the browser first."
    exit 1
fi