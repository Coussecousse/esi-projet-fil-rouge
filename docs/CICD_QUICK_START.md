# CI/CD Quick Start - For Local/Cloud Deployment

## 🎯 Choose Your Deployment Strategy

You have **3 options** for setting up CI/CD:

### **Option 1: Skip CI/CD for Now (Recommended for Testing)**

Just use your local Docker setup:
```bash
./start-microservices.sh
```
Access at: http://localhost:3000/

**When to use:** You're still developing and don't have servers yet.

---

### **Option 2: Deploy to Cloud Servers (AWS, Azure, GCP)**

If you have cloud servers, use their IP addresses:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy

# Copy to your ACTUAL servers (replace with your IPs)
ssh-copy-id -i ~/.ssh/github_deploy.pub ubuntu@3.15.123.45    # DEV server
ssh-copy-id -i ~/.ssh/github_deploy.pub ubuntu@18.220.67.89  # STAGING server
ssh-copy-id -i ~/.ssh/github_deploy.pub ubuntu@52.14.98.123  # PROD server
```

**Then configure GitHub Secrets with:**
- `DEV_HOST`: `3.15.123.45` (your dev server IP)
- `DEV_USER`: `ubuntu` (or `ec2-user`, `deploy`, etc.)
- `DEV_SSH_KEY`: (content of `~/.ssh/github_deploy`)

---

### **Option 3: Deploy to Local VMs/Servers**

If you have local servers with domain names:

```bash
# Add to /etc/hosts (if using local names)
sudo nano /etc/hosts

# Add lines like:
192.168.1.100  dev.medisecure.local
192.168.1.101  staging.medisecure.local
192.168.1.102  prod.medisecure.local

# Then copy SSH keys
ssh-copy-id -i ~/.ssh/github_deploy.pub deploy@192.168.1.100
```

---

## 🚀 Simplified Setup for Beginners

### **If You Don't Have Servers Yet:**

1. **Skip the CI/CD for now** - just develop locally
2. Push your code to GitHub normally
3. Set up servers later when you're ready to deploy

### **If You Have One Server:**

Use the **same server** for all 3 environments:

**GitHub Secrets Configuration:**
```
DEV_HOST = your-server.com (or IP: 54.123.45.67)
DEV_USER = ubuntu
DEV_SSH_KEY = (your private key)

STAGING_HOST = your-server.com (same as DEV)
STAGING_USER = ubuntu
STAGING_SSH_KEY = (same key)

PROD_HOST = your-server.com (same as DEV)
PROD_USER = ubuntu
PROD_SSH_KEY = (same key)
```

The pipeline will still work - it just deploys everything to the same server.

---

## 📝 Step-by-Step: Complete Setup

### **Step 1: Get a Server** (Choose one)

**Cloud Options:**
- **AWS EC2**: Free tier available → https://aws.amazon.com/free/
- **DigitalOcean**: $6/month → https://www.digitalocean.com/
- **Azure**: Free tier → https://azure.microsoft.com/free/
- **Google Cloud**: Free tier → https://cloud.google.com/free
- **Oracle Cloud**: Always free tier → https://www.oracle.com/cloud/free/

**Local Options:**
- VirtualBox VM on your laptop
- Old laptop/desktop as a server
- Raspberry Pi

### **Step 2: Generate SSH Key**

```bash
# Generate key pair
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy

# You'll have 2 files:
# ~/.ssh/github_deploy (PRIVATE - for GitHub)
# ~/.ssh/github_deploy.pub (PUBLIC - for server)
```

### **Step 3: Copy Key to Server**

```bash
# Replace USER@SERVER with your actual values
ssh-copy-id -i ~/.ssh/github_deploy.pub ubuntu@54.123.45.67

# Or manually:
cat ~/.ssh/github_deploy.pub | ssh ubuntu@54.123.45.67 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### **Step 4: Configure GitHub Secrets**

Go to: https://github.com/Coussecousse/esi-projet-fil-rouge/settings/secrets/actions

**For EACH environment, add 3 secrets:**

**Development:**
```
Name: DEV_HOST
Value: 54.123.45.67 (YOUR server IP or domain)

Name: DEV_USER  
Value: ubuntu (or ec2-user, deploy, etc.)

Name: DEV_SSH_KEY
Value: (paste content of ~/.ssh/github_deploy - the PRIVATE key)
```

**To get private key content:**
```bash
cat ~/.ssh/github_deploy
```
Copy EVERYTHING including `-----BEGIN` and `-----END` lines.

**Repeat for STAGING and PROD** (can be same server if you only have one).

### **Step 5: Configure GitHub Environments**

Go to: https://github.com/Coussecousse/esi-projet-fil-rouge/settings/environments

Create 3 environments:
1. `development` - no protection
2. `staging` - no protection  
3. `production` - add required reviewers

### **Step 6: Prepare Server**

SSH to your server and run:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Logout and login again, then:

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create directory
sudo mkdir -p /opt/medisecure
sudo chown $USER:$USER /opt/medisecure
cd /opt/medisecure

# Clone your repo
git clone https://github.com/Coussecousse/esi-projet-fil-rouge.git .

# Make scripts executable
chmod +x *.sh
chmod +x kong/configure-kong.sh
```

### **Step 7: Test It!**

```bash
# On your LOCAL machine:
git checkout develop
git add .
git commit -m "test: CI/CD setup"
git push origin develop

# Watch deployment at:
# https://github.com/Coussecousse/esi-projet-fil-rouge/actions
```

---

## 🆘 Troubleshooting

### "Could not resolve hostname"
- You're using example hostnames that don't exist
- Replace with your actual server IP or domain name

### "Permission denied (publickey)"
- SSH key not copied to server correctly
- Run: `ssh-copy-id -i ~/.ssh/github_deploy.pub USER@SERVER`
- Or check: `ssh -i ~/.ssh/github_deploy USER@SERVER` works manually

### "No such host"
- Wrong IP address or server is offline
- Test with: `ping YOUR_SERVER_IP`

### Don't have a server yet?
- **Just develop locally** with `./start-microservices.sh`
- Push code to GitHub normally
- Set up CI/CD later when you have servers

---

## 📋 Current Status Check

Run this to see what you have:

```bash
# Check if SSH key exists
ls -la ~/.ssh/github_deploy*

# Check if you can reach your server
ping YOUR_SERVER_IP

# Check if SSH works
ssh -i ~/.ssh/github_deploy USER@YOUR_SERVER_IP

# Check current running services (local)
docker-compose -f compose.yml ps
```

---

## ✅ Minimal Working Setup

**Absolute minimum to get started:**

1. **One server** (cloud or local) with Docker installed
2. **SSH key** generated and copied to server
3. **GitHub Secrets** configured (all pointing to same server is fine)
4. **GitHub Environments** created
5. **Push to develop branch** → auto deploys

You can use the SAME server for DEV, STAGING, and PROD initially. Just set all 3 sets of secrets to point to the same server.

---

## 🎓 What You Need to Know

**If you're new to servers:**
- Server = a computer running 24/7 that hosts your application
- IP address = like a phone number for computers (e.g., 54.123.45.67)
- Domain = friendly name that points to IP (e.g., myapp.com)
- SSH = secure way to control a remote server
- SSH key = password replacement (more secure)

**You don't need:**
- Domain name (IP address works fine)
- Multiple servers (one server can host all environments)
- Professional hosting (free tier cloud or local VM works)

---

## 🎯 Next Steps

1. **Do you have a server?**
   - YES → Follow Step 2-7 above
   - NO → Continue developing locally, deploy later

2. **Want to test locally first?**
   ```bash
   ./start-microservices.sh
   # Access at http://localhost:3000/
   ```

3. **Ready for cloud?**
   - Get free AWS/Azure/GCP account
   - Launch one small VM (t2.micro on AWS is free)
   - Follow Step 2-7 above

**Questions?** Check the full guide: `docs/CICD_SETUP.md`
