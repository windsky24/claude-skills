# Docker 常用指令參考

## 建立 Image

```bash
bash Docker/BuildGameImage.sh \
  {GameName}.tar.gz SlotCommon.tar.gz SlotServer.tar.gz \
  {codename} {version} Dockerfile
```

範例（ChaChaCha 0.0.7）：
```bash
bash Docker/BuildGameImage.sh \
  ChaChaCha.tar.gz SlotCommon.tar.gz SlotServer.tar.gz \
  chachacha 0.0.7 Dockerfile
```

---

## 服務管理

```bash
# 查看所有 image（確認建立成功 + 取得 image ID）
sudo docker image ls

# 啟動指定版本的服務（加 -d 背景執行）
sudo TAG=0.0.7 docker compose -f ./Docker/docker-compose.yml up -d

# 停止指定版本的服務
sudo TAG=0.0.7 docker compose -f ./Docker/docker-compose.yml down

# 查看所有容器狀態
docker ps -a
```

---

## 除錯與 Log

```bash
# 查看系統 Log（即時）
sudo tail -f /var/log/syslog

# 查看特定容器的 Log（codename 需小寫）
sudo docker logs docker-{codename}-1

# 範例：
sudo docker logs docker-chachacha-1
```

---

## 清理

```bash
# 刪除指定 image（先取得 image ID）
sudo docker rmi -f {image_id}

# 範例：
sudo docker rmi -f 6fd74c7a2f93
```

---

## 注意事項

1. **更新版本前**：必須先 `down` 舊版本才能 `up` 新版本
2. **Log 檔清除**：每次打包前確認 Log 檔與舊設定檔已清除，否則可能影響新版行為
3. **Tag 一致性**：BuildGameImage 的版本號需與 docker compose 的 TAG 一致
4. **codename 小寫**：docker-compose 的 service 名稱通常為小寫 codename

---

## 從跳板機部署完整流程

```bash
# 1. 在跳板機：將 tar.gz 傳到測試機家目錄
scp {GameName}.tar.gz SlotCommon.tar.gz SlotServer.tar.gz macross-slot-01-test:~

# 2. SSH 登入測試機
ssh macross-slot-01-test

# 3. 切換到遊戲目錄，複製 tar.gz
cd /path/to/game/directory
sudo cp ~/*.tar.gz ./

# 4. 建立 image
bash Docker/BuildGameImage.sh {GameName}.tar.gz SlotCommon.tar.gz SlotServer.tar.gz {codename} {version} Dockerfile

# 5. 確認 image 建立成功
sudo docker images

# 6. 啟動服務
sudo TAG={version} docker compose -f ./Docker/docker-compose.yml up -d
```
