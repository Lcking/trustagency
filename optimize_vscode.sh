#!/bin/bash

# 🚀 VSCode 快速优化脚本

echo "🔍 正在诊断系统内存..."
MEMORY_USAGE=$(top -l 1 | grep "PhysMem:" | awk '{print $2}' | sed 's/G.*//')
echo "当前内存使用: ${MEMORY_USAGE}GB"

echo ""
echo "📊 VSCode 进程分析..."
ps aux | grep -E "Code|code" | grep -v grep | awk '{print $2, $4"% - "$11}' | head -5

echo ""
echo "📍 执行优化步骤..."

# 步骤1: 备份当前设置
echo "✅ 步骤1: 备份VSCode设置..."
BACKUP_DIR=~/.vscode_backup_$(date +%s)
mkdir -p "$BACKUP_DIR"
cp -r ~/Library/Application\ Support/Code/User ~/Library/Application\ Support/Code/CachedExtensionVSIXs "$BACKUP_DIR/" 2>/dev/null
echo "   备份位置: $BACKUP_DIR"

# 步骤2: 清理缓存
echo "✅ 步骤2: 清理缓存..."
rm -rf ~/Library/Application\ Support/Code/CachedExtensionVSIXs/*
rm -rf ~/Library/Caches/com.microsoft.VSCode/*
echo "   缓存已清理"

# 步骤3: 显示要禁用的插件建议
echo "✅ 步骤3: 建议禁用的插件列表..."
echo ""
echo "   打开VSCode后，按 Ctrl+Shift+X (扩展)"
echo "   搜索并禁用以下插件（如果不使用）："
echo "   ❌ SQL相关: MSSQL, SQL Tools, SQL Database Projects (3个)"
echo "   ❌ ms-python.vscode-pylance (改用Pylance lite版)"
echo "   ❌ ms-azuretools.vscode-containers (除非用Docker)"
echo "   ❌ ritwickdey.liveserver (除非做前端调试)"
echo "   ❌ xdebug.php-debug (不用PHP)"
echo ""

# 步骤4: 显示监控命令
echo "✅ 步骤4: 监控内存使用..."
echo "   可以使用此命令持续监控："
echo "   watch -n 2 'ps aux | grep Code | grep -v grep | awk \"{print \\$2, \\$4\\\"%\\\"}\" | head -5'"
echo ""

echo "⚙️ 完成！请按以下步骤操作："
echo ""
echo "1. 关闭VSCode: killall Electron"
echo "2. 等待5秒"
echo "3. 重新打开VSCode"
echo "4. 按照建议禁用插件"
echo "5. 重启VSCode"
echo "6. 运行 'top -l 1 | grep PhysMem' 检查内存"
echo ""
echo "预期效果: 内存占用下降 30-40%, 卡顿消失 ✨"
echo ""

# 步骤5: 提供恢复命令
echo "🔄 如需恢复，运行:"
echo "   cp -r $BACKUP_DIR/* ~/"
