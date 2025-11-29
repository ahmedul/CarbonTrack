#!/usr/bin/env python3
"""
Update CloudFront distribution with optimized settings
"""
import json
import subprocess
import sys

def run_command(cmd):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout

def main():
    distribution_id = "EUKA4HQFK6MC"
    
    print("📥 Getting current CloudFront configuration...")
    
    # Get current config
    config_output = run_command(f"aws cloudfront get-distribution-config --id {distribution_id}")
    if not config_output:
        sys.exit(1)
    
    config_data = json.loads(config_output)
    etag = config_data['ETag']
    config = config_data['DistributionConfig']
    
    print(f"✅ Current ETag: {etag}")
    print(f"📝 Current settings:")
    print(f"   - Viewer Protocol: {config['DefaultCacheBehavior']['ViewerProtocolPolicy']}")
    print(f"   - Compress: {config['DefaultCacheBehavior']['Compress']}")
    
    # Update settings
    print("\n🔧 Updating settings...")
    config['DefaultCacheBehavior']['ViewerProtocolPolicy'] = 'redirect-to-https'
    config['DefaultCacheBehavior']['Compress'] = True
    
    # Add custom error responses for SPA routing
    config['CustomErrorResponses'] = {
        'Quantity': 2,
        'Items': [
            {
                'ErrorCode': 403,
                'ResponsePagePath': '/index.html',
                'ResponseCode': '200',
                'ErrorCachingMinTTL': 300
            },
            {
                'ErrorCode': 404,
                'ResponsePagePath': '/index.html',
                'ResponseCode': '200',
                'ErrorCachingMinTTL': 300
            }
        ]
    }
    
    # Save updated config
    with open('/tmp/cloudfront-update.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration file created: /tmp/cloudfront-update.json")
    print("\n🚀 Applying changes to CloudFront...")
    
    # Update distribution
    update_cmd = f"aws cloudfront update-distribution --id {distribution_id} --if-match {etag} --distribution-config file:///tmp/cloudfront-update.json"
    result = run_command(update_cmd)
    
    if result:
        print("✅ CloudFront distribution updated successfully!")
        print("\n📋 New settings:")
        print("   ✅ HTTPS redirect enabled (secure)")
        print("   ✅ Compression enabled (faster)")
        print("   ✅ SPA routing fixed (403/404 → index.html)")
        print(f"\n🌐 Your CDN URL: https://d2z2og1o0b9esb.cloudfront.net")
        print("\n⏳ Changes will deploy in ~5-10 minutes")
    else:
        print("❌ Failed to update distribution")
        sys.exit(1)

if __name__ == '__main__':
    main()
