#!/bin/bash
# 快速诊断脚本 - 检查服务器当前状态

SERVER_IP="106.13.188.99"

echo "🔍 快速诊断服务器状态"
echo "========================"
echo ""

echo "📍 服务器: $SERVER_IP"
echo ""

echo "1️⃣  检查 /root 目录:"
ssh root@${SERVER_IP} 'ls -la /root/ | grep -E "^d" | awk "{print $NF}"' || echo "   (无法连接)"

echo ""
echo "2️⃣  检查 /root/trustagency* 是否存在:"
ssh root@${SERVER_IP} '[ -d "/root/trustagency" ] && echo "✅ /root/trustagency 存在" || echo "❌ /root/trustagency 不存在"' || echo "   (无法连接)"

echo ""
echo "3️⃣  检查 Docker 容器:"
ssh root@${SERVER_IP} 'docker ps -a --format "{{.Names}}" 2>/dev/null' || echo "   (无法连接或 Docker 不可用)"

echo ""
echo "4️⃣  检查 Docker 卷:"
ssh root@${SERVER_IP} 'docker volume ls 2>/dev/null | tail -5' || echo "   (无法连接或 Docker 不可用)"

echo ""
echo "5️⃣  查找所有 trustagency 相关文件:"
ssh root@${SERVER_IP} 'find / -name "*trustagency*" -type d 2>/dev/null | head -10' || echo "   (无法连接)"

echo ""
echo "========================"
echo "✅ 诊断完成"
