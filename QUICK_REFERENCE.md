# TechXConf Quiz App - Quick Reference

## 🚀 ONE-COMMAND SETUP

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

### Mac/Linux

```bash
chmod +x setup.sh && ./setup.sh
```

## 🌐 ACCESS THE APPLICATION

| Service      | URL                        | Purpose                       |
| ------------ | -------------------------- | ----------------------------- |
| **Quiz App** | http://localhost:3000      | Main application interface    |
| **API**      | http://localhost:8000      | Backend REST API              |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |

## 🔐 LOGIN CREDENTIALS

**Admin Account:**

- Email: `admin@example.com`
- Password: `Admin123!`

## 📊 CURRENT STATUS

✅ **428 Questions Loaded** across multiple topics:

- AI & Machine Learning
- Cloud Computing
- Relational Databases
- And more...

## 🎯 COMMON TASKS

### View Logs

```bash
docker compose -f docker-compose.local.yml logs -f
```

### Stop Application

```bash
docker compose -f docker-compose.local.yml down
```

### Restart Application

```bash
docker compose -f docker-compose.local.yml restart
```

### Import More Questions

```bash
docker compose -f docker-compose.local.yml exec backend python scripts/import_xlsx.py your_file.xlsx
```

### Check Service Status

```bash
docker compose -f docker-compose.local.yml ps
```

## 📁 FILES CREATED

- `setup.ps1` - Windows PowerShell setup script
- `setup.sh` - Mac/Linux Bash setup script
- `QUICKSTART.md` - Comprehensive quick start guide
- `.env` - Environment configuration (auto-created)

## 🎓 USING THE APP

1. **Register/Login** at http://localhost:3000
2. **Browse Quizzes** - View available topics
3. **Take a Quiz** - Select questions and difficulty
4. **View Results** - See scores and explanations
5. **Check Leaderboard** - Compare with others

## 🆘 TROUBLESHOOTING

**Ports in use?**

- Stop other services on ports 3000, 5432, 6379, 8000

**Services not starting?**

- Check Docker is running
- View logs: `docker compose -f docker-compose.local.yml logs`

**No questions showing?**

- Questions are already imported (428 total)
- Re-run: `docker compose -f docker-compose.local.yml exec backend python scripts/import_xlsx.py Cloud_AI_Quiz_450.xlsx`

## 📚 MORE HELP

See `QUICKSTART.md` for detailed documentation and troubleshooting.

---

**Enjoy your quiz application!** 🎉
