#!/usr/bin/env pwsh

# ============================================
# CLI MODE - Accept feature number as argument
# ============================================
param(
    [int]$Feature = 0,
    [string]$Path = "",
    [string]$Source = "",
    [string]$Destination = "",
    [string]$Device = "",
    [string]$IsoPath = "",
    [string]$Filesystem = "ext4",
    [string]$Label = "",
    [switch]$SearchContent = $false
)

# ============================================
# FUNCTIONS SECTION
# ============================================

function Show-Menu {
    Clear-Host
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                              ║" -ForegroundColor Cyan
    Write-Host "║            KALI SMARTOPS MANAGER PRO - CONSOLE               ║" -ForegroundColor Yellow
    Write-Host "║                    System Administration Tool                ║" -ForegroundColor Green
    Write-Host "║                                                              ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "┌─────────────────────────────────────────────────────────────┐" -ForegroundColor Magenta
    Write-Host "│                    MAIN MENU                                │" -ForegroundColor Magenta
    Write-Host "├─────────────────────────────────────────────────────────────┤" -ForegroundColor Magenta
    Write-Host "│  1. 📊 System Information                                   │" -ForegroundColor Green
    Write-Host "│  2. 🔍 Process Monitor (Top 15)                            │" -ForegroundColor Green
    Write-Host "│  3. 📈 Real-time System Monitor                             │" -ForegroundColor Green
    Write-Host "│  4. 🌐 Network Interfaces & Connections                     │" -ForegroundColor Green
    Write-Host "│  5. 📡 Bandwidth Usage Statistics                           │" -ForegroundColor Green
    Write-Host "│  6. 🔒 Port Scan (Listening Ports)                          │" -ForegroundColor Green
    Write-Host "│  7. 🔄 Service Manager (Running/Failed)                     │" -ForegroundColor Green
    Write-Host "│  8. 💾 Disk Usage Analysis                                  │" -ForegroundColor Green
    Write-Host "│  9. 🧹 System Cleanup Tools                                 │" -ForegroundColor Green
    Write-Host "│ 10. 🔐 Security Check (Suspicious Processes)                │" -ForegroundColor Green
    Write-Host "│ 11. 📦 Package Manager Updates                              │" -ForegroundColor Green
    Write-Host "│ 12. 💻 Hardware Information                                 │" -ForegroundColor Green
    Write-Host "│ 13. 📁 File Manager                                         │" -ForegroundColor Green
    Write-Host "│ 14. 💿 Bootable Drive Creator                               │" -ForegroundColor Green
    Write-Host "│ 15. 💾 Storage Format                                       │" -ForegroundColor Green
    Write-Host "│  0. ❌ Exit                                                 │" -ForegroundColor Red
    Write-Host "└─────────────────────────────────────────────────────────────┘" -ForegroundColor Magenta
    Write-Host ""
}

function Show-SystemInfo {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    SYSTEM INFORMATION                         ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "▶ OPERATING SYSTEM:" -ForegroundColor Yellow
    $osInfo = & lsb_release -d 2>$null | cut -f2
    if (-not $osInfo) {
        $osInfo = & cat /etc/os-release 2>$null | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '"'
    }
    Write-Host "   $osInfo" -ForegroundColor White
    
    Write-Host "`n▶ KERNEL:" -ForegroundColor Yellow
    Write-Host "   $(uname -a)" -ForegroundColor White
    
    Write-Host "`n▶ UPTIME:" -ForegroundColor Yellow
    $uptime = & uptime -p 2>$null
    if (-not $uptime) { $uptime = & uptime }
    Write-Host "   $uptime" -ForegroundColor White
    
    Write-Host "`n▶ CPU INFORMATION:" -ForegroundColor Yellow
    $cpuModel = & lscpu 2>$null | grep "Model name" | cut -d':' -f2 | xargs
    Write-Host "   Model: $cpuModel" -ForegroundColor White
    $cpuCores = & nproc 2>$null
    if (-not $cpuCores) { $cpuCores = & grep -c ^processor /proc/cpuinfo }
    Write-Host "   Cores: $cpuCores" -ForegroundColor White
    Write-Host "   Architecture: $(uname -m)" -ForegroundColor White
    
    Write-Host "`n▶ MEMORY USAGE:" -ForegroundColor Yellow
    & free -h | grep -E "^(Mem|Swap)" | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    
    Write-Host "`n▶ DISK USAGE:" -ForegroundColor Yellow
    & df -h | grep -E "^/dev/" | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    
    Write-Host "`n▶ ACTIVE USERS:" -ForegroundColor Yellow
    & who | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
}

function Show-ProcessMonitor {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║              TOP 15 PROCESSES BY CPU & MEMORY                  ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host ("{0,-8} {1,-25} {2,-10} {3,-10} {4,-15}" -f "PID", "PROCESS", "CPU%", "MEM%", "USER") -ForegroundColor Yellow
    Write-Host ("{0,-8} {1,-25} {2,-10} {3,-10} {4,-15}" -f "---", "-------", "----", "----", "----") -ForegroundColor DarkGray
    
    $processes = & ps -eo pid,comm,%cpu,%mem,user --sort=-%cpu 2>$null | head -16
    if (-not $processes) {
        $processes = & ps aux 2>$null | sort -k3 -rn | head -16
    }
    
    $processes | Select-Object -Skip 1 | ForEach-Object {
        $fields = $_ -split '\s+', 5
        if ($fields.Count -ge 5) {
            Write-Host ("{0,-8} {1,-25} {2,-10} {3,-10} {4,-15}" -f $fields[0], $fields[1], $fields[2], $fields[3], $fields[4]) -ForegroundColor White
        }
    }
    
    $totalProc = & ps -e 2>$null | Measure-Object -Line | Select-Object -ExpandProperty Lines
    Write-Host "`n📊 Total Running Processes: $totalProc" -ForegroundColor Green
}

function Show-RealtimeMonitor {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                 REAL-TIME SYSTEM METRICS                       ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    $cpuLine = & top -bn1 2>$null | grep "Cpu(s)"
    if (-not $cpuLine) { $cpuLine = & top -bn1 2>$null | grep "%Cpu" }
    
    if ($cpuLine -match "([0-9.]+)%") {
        $cpuLoad = $matches[1]
    } else {
        $cpuLoad = "0"
    }
    
    Write-Host "▶ CPU USAGE:" -ForegroundColor Yellow
    $cpuInt = [int][math]::Floor($cpuLoad)
    if ($cpuInt -gt 80) {
        Write-Host "   ⚠️  ${cpuLoad}% (HIGH USAGE!)" -ForegroundColor Red
    } elseif ($cpuInt -gt 60) {
        Write-Host "   ⚡ ${cpuLoad}% (Moderate)" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ ${cpuLoad}% (Normal)" -ForegroundColor Green
    }
    
    $memInfo = & free 2>$null | grep Mem
    if ($memInfo) {
        $memParts = $memInfo -split '\s+'
        $memTotal = $memParts[1]
        $memUsed = $memParts[2]
        $memUsage = [math]::Round(($memUsed / $memTotal) * 100, 1)
        
        Write-Host "`n▶ MEMORY USAGE:" -ForegroundColor Yellow
        if ($memUsage -gt 90) {
            Write-Host "   ⚠️  $memUsage% (CRITICAL!)" -ForegroundColor Red
        } elseif ($memUsage -gt 75) {
            Write-Host "   ⚡ $memUsage% (High)" -ForegroundColor Yellow
        } else {
            Write-Host "   ✅ $memUsage% (Normal)" -ForegroundColor Green
        }
    }
    
    $diskInfo = & df -h / 2>$null | tail -1
    if ($diskInfo) {
        $diskParts = $diskInfo -split '\s+'
        $diskUsage = $diskParts[4] -replace '%',''
        
        Write-Host "`n▶ DISK USAGE (/):" -ForegroundColor Yellow
        $diskInt = [int]$diskUsage
        if ($diskInt -gt 85) {
            Write-Host "   ⚠️  ${diskUsage}% (LOW SPACE!)" -ForegroundColor Red
        } elseif ($diskInt -gt 70) {
            Write-Host "   ⚡ ${diskUsage}% (Getting Full)" -ForegroundColor Yellow
        } else {
            Write-Host "   ✅ ${diskUsage}% (Good)" -ForegroundColor Green
        }
    }
    
    $loadAvg = & uptime 2>$null
    if ($loadAvg) {
        Write-Host "`n▶ LOAD AVERAGE:" -ForegroundColor Yellow
        Write-Host "   $loadAvg" -ForegroundColor White
    }
}

function Show-NetworkInfo {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                   NETWORK INTERFACES                           ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "▶ ACTIVE NETWORK INTERFACES:" -ForegroundColor Yellow
    $interfaces = & ip -br addr show 2>$null
    if ($interfaces) {
        $interfaces | ForEach-Object {
            if ($_ -match "UP") {
                Write-Host "   ✅ $_" -ForegroundColor Green
            } else {
                Write-Host "   ❌ $_" -ForegroundColor Red
            }
        }
    }
    
    Write-Host "`n▶ ACTIVE CONNECTIONS:" -ForegroundColor Yellow
    $connCount = & ss -tuln 2>$null | Measure-Object -Line | Select-Object -ExpandProperty Lines
    Write-Host "   $connCount listening ports" -ForegroundColor White
    
    Write-Host "`n▶ DETAILED CONNECTIONS (First 20):" -ForegroundColor Yellow
    & ss -tuln 2>$null | Select-Object -First 20 | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
}

function Show-Bandwidth {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                   BANDWIDTH STATISTICS                         ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    $interfaces = & ip -br link 2>$null | grep -v LOOPBACK | awk '{print $1}'
    
    foreach ($iface in $interfaces) {
        $rx_bytes = & cat "/sys/class/net/$iface/statistics/rx_bytes" 2>$null
        $tx_bytes = & cat "/sys/class/net/$iface/statistics/tx_bytes" 2>$null
        
        if ($rx_bytes -and $tx_bytes) {
            $rx_gb = [math]::Round($rx_bytes / 1024 / 1024 / 1024, 2)
            $tx_gb = [math]::Round($tx_bytes / 1024 / 1024 / 1024, 2)
            
            Write-Host "▶ INTERFACE: $iface" -ForegroundColor Yellow
            Write-Host "   📥 Received: $rx_gb GB" -ForegroundColor White
            Write-Host "   📤 Transmitted: $tx_gb GB" -ForegroundColor White
            Write-Host ""
        }
    }
}

function Show-PortScan {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                   LISTENING PORTS                              ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "▶ OPEN PORTS (LISTENING):" -ForegroundColor Yellow
    $ports = & ss -tuln 2>$null | grep LISTEN | awk '{print $5}' | cut -d':' -f2 | sort -n | uniq
    $ports | ForEach-Object {
        $port = $_
        $service = switch ($port) {
            "22" { "SSH" }
            "80" { "HTTP" }
            "443" { "HTTPS" }
            "3306" { "MySQL" }
            "5432" { "PostgreSQL" }
            "8080" { "HTTP-Alt" }
            "53" { "DNS" }
            "25" { "SMTP" }
            "21" { "FTP" }
            default { "Unknown" }
        }
        Write-Host "   🔌 Port $port - $service" -ForegroundColor Green
    }
    
    Write-Host "`n▶ DETAILED LISTENING SERVICES:" -ForegroundColor Yellow
    & ss -tuln 2>$null | grep LISTEN | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
}

function Show-ServiceManager {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    SERVICE MANAGER                             ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "▶ RUNNING SERVICES (First 20):" -ForegroundColor Green
    $running = & systemctl list-units --type=service --state=running 2>$null | head -20
    if ($running) {
        $running | ForEach-Object { Write-Host "   ✅ $_" -ForegroundColor White }
    } else {
        Write-Host "   ⚠️  No running services found or systemctl not available" -ForegroundColor Yellow
    }
    
    Write-Host "`n▶ FAILED SERVICES:" -ForegroundColor Red
    $failed = & systemctl --failed 2>$null | grep -E "^●" | head -10
    if ($failed) {
        $failed | ForEach-Object { Write-Host "   ❌ $_" -ForegroundColor Red }
    } else {
        Write-Host "   ✅ No failed services found" -ForegroundColor Green
    }
}

function Show-DiskAnalysis {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                   DISK USAGE ANALYSIS                          ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "▶ LARGEST DIRECTORIES IN /HOME (Top 10):" -ForegroundColor Yellow
    $homeDirs = & du -h /home 2>$null | sort -rh | head -10
    if ($homeDirs) {
        $homeDirs | ForEach-Object { Write-Host "   📁 $_" -ForegroundColor White }
    } else {
        Write-Host "   No home directories found or insufficient permissions" -ForegroundColor Gray
    }
    
    Write-Host "`n▶ LARGEST DIRECTORIES IN CURRENT DIRECTORY (Top 10):" -ForegroundColor Yellow
    & du -h --max-depth=2 2>$null | sort -rh | head -10 | ForEach-Object { Write-Host "   📁 $_" -ForegroundColor White }
    
    Write-Host "`n▶ DISK USAGE BY FILE TYPE:" -ForegroundColor Yellow
    Write-Host "   Videos: $(find . -name '*.mp4' -o -name '*.avi' -o -name '*.mkv' 2>$null | wc -l) files" -ForegroundColor White
    Write-Host "   Images: $(find . -name '*.jpg' -o -name '*.png' -o -name '*.gif' 2>$null | wc -l) files" -ForegroundColor White
    Write-Host "   Documents: $(find . -name '*.pdf' -o -name '*.doc' -o -name '*.txt' 2>$null | wc -l) files" -ForegroundColor White
    Write-Host "   Archives: $(find . -name '*.zip' -o -name '*.tar.gz' -o -name '*.rar' 2>$null | wc -l) files" -ForegroundColor White
}

function Show-CleanupTools {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    SYSTEM CLEANUP TOOLS                        ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    $cacheSize = & du -sh /var/cache/apt/archives 2>$null | awk '{print $1}'
    if (-not $cacheSize) { $cacheSize = "0B" }
    Write-Host "▶ PACKAGE CACHE:" -ForegroundColor Yellow
    Write-Host "   Size: $cacheSize" -ForegroundColor White
    
    $logCount = & find /var/log -name "*.log" -mtime +30 2>$null | wc -l
    Write-Host "`n▶ OLD LOG FILES (>30 days):" -ForegroundColor Yellow
    Write-Host "   Files found: $logCount" -ForegroundColor White
    
    $tmpSize = & du -sh /tmp 2>$null | awk '{print $1}'
    Write-Host "`n▶ TEMPORARY FILES:" -ForegroundColor Yellow
    Write-Host "   /tmp size: $tmpSize" -ForegroundColor White
    
    $trashSize = & du -sh ~/.local/share/Trash 2>$null | awk '{print $1}'
    Write-Host "`n▶ TRASH SIZE:" -ForegroundColor Yellow
    Write-Host "   $trashSize" -ForegroundColor White
}

function Show-SecurityCheck {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    SECURITY CHECK                              ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "▶ SUSPICIOUS PROCESSES (High CPU > 80%):" -ForegroundColor Yellow
    $highCpu = & ps -eo pid,comm,%cpu --sort=-%cpu 2>$null | head -10
    $foundHighCpu = $false
    $highCpu | ForEach-Object {
        if ($_ -match "([8-9][0-9]|100)") {
            Write-Host "   ⚠️  $_" -ForegroundColor Red
            $foundHighCpu = $true
        } else {
            if ($_ -notmatch "PID") {
                Write-Host "   $_" -ForegroundColor White
            }
        }
    }
    if (-not $foundHighCpu) { Write-Host "   ✅ No suspicious high-CPU processes found" -ForegroundColor Green }
    
    Write-Host "`n▶ LAST LOGINS (First 10):" -ForegroundColor Yellow
    & last -n 10 2>$null | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
}

function Show-PackageUpdates {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    PACKAGE UPDATES                             ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "▶ UPDATING PACKAGE LIST..." -ForegroundColor Yellow
    & sudo apt-get update 2>&1 | tail -5
    
    Write-Host "`n▶ AVAILABLE UPDATES:" -ForegroundColor Yellow
    $updates = & apt list --upgradable 2>$null | grep -v "Listing" | Select-Object -First 20
    if ($updates) {
        $updates | ForEach-Object { Write-Host "   📦 $_" -ForegroundColor White }
        $updateCount = ($updates | Measure-Object -Line).Lines
        Write-Host "`n📊 Total updates available: $updateCount" -ForegroundColor Green
    } else {
        Write-Host "   ✅ System is up to date!" -ForegroundColor Green
    }
}

function Show-HardwareInfo {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                   HARDWARE INFORMATION                         ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "▶ CPU DETAILS:" -ForegroundColor Yellow
    & lscpu 2>$null | grep -E "^(Model name|Architecture|CPU\(s\)|Thread|Core|Socket|Virtualization)" | ForEach-Object {
        Write-Host "   $_" -ForegroundColor White
    }
    
    Write-Host "`n▶ MEMORY DETAILS:" -ForegroundColor Yellow
    & free -h | head -2 | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    
    Write-Host "`n▶ BLOCK DEVICES (Drives):" -ForegroundColor Yellow
    & lsblk 2>$null | grep -v "loop" | head -15 | ForEach-Object { Write-Host "   💾 $_" -ForegroundColor White }
    
    Write-Host "`n▶ GRAPHICS CARD:" -ForegroundColor Yellow
    & lspci 2>$null | grep -i "vga" | ForEach-Object { Write-Host "   🖥️  $_" -ForegroundColor White }
    
    Write-Host "`n▶ NETWORK CARDS:" -ForegroundColor Yellow
    & lspci 2>$null | grep -i "network" | ForEach-Object { Write-Host "   🌐 $_" -ForegroundColor White }
}

# ============================================
# FILE MANAGER FUNCTIONS (Features 13-19)
# ============================================

function Get-FileList {
    param([string]$Directory)
    
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    FILE LIST                                  ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📍 Directory: $Directory" -ForegroundColor Yellow
    Write-Host ""
    Write-Host ("{0,-10} {1,-35} {2,-15} {3,-20}" -f "TYPE", "NAME", "SIZE", "MODIFIED") -ForegroundColor Green
    Write-Host ("{0,-10} {1,-35} {2,-15} {3,-20}" -f "----", "----", "----", "--------") -ForegroundColor DarkGray
    
    $items = Get-ChildItem -Path $Directory -ErrorAction SilentlyContinue
    foreach ($item in $items) {
        $type = if ($item.PSIsContainer) { "📁 DIR" } else { "📄 FILE" }
        $size = if ($item.PSIsContainer) { "-" } else { "{0:N2} KB" -f ($item.Length / 1KB) }
        $modified = $item.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
        $name = if ($item.Name.Length -gt 32) { $item.Name.Substring(0,29) + "..." } else { $item.Name }
        Write-Host ("{0,-10} {1,-35} {2,-15} {3,-20}" -f $type, $name, $size, $modified) -ForegroundColor White
    }
    Write-Host ""
    Write-Host "📊 Total items: $($items.Count)" -ForegroundColor Green
}

function Copy-ItemPS {
    param([string]$Source, [string]$Destination)
    
    Write-Host "`n📋 Copying..." -ForegroundColor Yellow
    Write-Host "   From: $Source" -ForegroundColor White
    Write-Host "   To: $Destination" -ForegroundColor White
    
    try {
        if (Test-Path $Source -PathType Container) {
            Copy-Item -Path $Source -Destination $Destination -Recurse -Force
        } else {
            Copy-Item -Path $Source -Destination $Destination -Force
        }
        Write-Host "✅ Successfully copied!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

function Move-ItemPS {
    param([string]$Source, [string]$Destination)
    
    Write-Host "`n✂️ Moving..." -ForegroundColor Yellow
    Write-Host "   From: $Source" -ForegroundColor White
    Write-Host "   To: $Destination" -ForegroundColor White
    
    try {
        Move-Item -Path $Source -Destination $Destination -Force
        Write-Host "✅ Successfully moved!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

function Delete-ItemPS {
    param([string]$Path)
    
    Write-Host "`n🗑️ Deleting..." -ForegroundColor Yellow
    Write-Host "   Path: $Path" -ForegroundColor White
    
    try {
        if (Test-Path $Path -PathType Container) {
            Remove-Item -Path $Path -Recurse -Force
        } else {
            Remove-Item -Path $Path -Force
        }
        Write-Host "✅ Successfully deleted!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

function Rename-ItemPS {
    param([string]$Path, [string]$NewName)
    
    $newPath = Join-Path (Split-Path $Path) $NewName
    Write-Host "`n✏️ Renaming..." -ForegroundColor Yellow
    Write-Host "   From: $(Split-Path $Path -Leaf)" -ForegroundColor White
    Write-Host "   To: $NewName" -ForegroundColor White
    
    try {
        Rename-Item -Path $Path -NewName $NewName -Force
        Write-Host "✅ Successfully renamed!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

function New-FolderPS {
    param([string]$Path)
    
    Write-Host "`n📁 Creating folder..." -ForegroundColor Yellow
    Write-Host "   Path: $Path" -ForegroundColor White
    
    try {
        New-Item -Path $Path -ItemType Directory -Force -ErrorAction Stop
        Write-Host "✅ Folder created successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

function Search-FilesPS {
    param([string]$Directory, [string]$Pattern, [switch]$SearchContent)
    
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    SEARCH RESULTS                             ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔍 Searching for: $Pattern" -ForegroundColor Yellow
    Write-Host "📍 Directory: $Directory" -ForegroundColor Yellow
    if ($SearchContent) { Write-Host "📄 Searching inside file content..." -ForegroundColor Cyan }
    Write-Host ""
    
    $found = 0
    if ($SearchContent) {
        $results = Get-ChildItem -Path $Directory -Recurse -File -ErrorAction SilentlyContinue | Select-String -Pattern $Pattern -SimpleMatch
        foreach ($result in $results) {
            Write-Host "📄 $($result.Path)" -ForegroundColor White
            Write-Host "   ↳ Line $($result.LineNumber): $($result.Line.Trim().Substring(0, [Math]::Min(80, $result.Line.Trim().Length)))" -ForegroundColor Gray
            $found++
            if ($found -ge 50) { Write-Host "   ... (showing first 50 results)" -ForegroundColor Yellow; break }
        }
    } else {
        $results = Get-ChildItem -Path $Directory -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*$Pattern*" }
        foreach ($item in $results) {
            $type = if ($item.PSIsContainer) { "📁" } else { "📄" }
            $size = if ($item.PSIsContainer) { "-" } else { "{0:N2} KB" -f ($item.Length / 1KB) }
            Write-Host "$type $($item.FullName) [$size]" -ForegroundColor White
            $found++
            if ($found -ge 100) { Write-Host "   ... (showing first 100 results)" -ForegroundColor Yellow; break }
        }
    }
    Write-Host ""
    Write-Host "📊 Found $found matches" -ForegroundColor Green
}

# ============================================
# FIXED: BOOTABLE DRIVE FUNCTIONS (Features 20-21) - LINUX COMPATIBLE
# ============================================

function Get-USBDrives {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    USB DRIVES                                 ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Use Linux lsblk command instead of Windows Get-Disk
    $usbInfo = & lsblk -d -o NAME,SIZE,MODEL,TYPE -n 2>$null
    
    $found = $false
    foreach ($line in $usbInfo) {
        if ($line -match "disk") {
            $parts = $line -split '\s+', 3
            if ($parts.Count -ge 2) {
                $name = $parts[0]
                $size = $parts[1]
                $model = if ($parts.Count -ge 3) { $parts[2] } else { "USB Drive" }
                
                # Skip main system drive (usually sda)
                if ($name -ne "sda" -and $name -ne "nvme0n1") {
                    Write-Host "💾 /dev/$name - ${size} - $model" -ForegroundColor Green
                    $found = $true
                }
            }
        }
    }
    
    if (-not $found) {
        Write-Host "⚠️ No USB drives detected" -ForegroundColor Yellow
        Write-Host "   Make sure a USB drive is connected" -ForegroundColor White
        Write-Host "   Tip: Run 'lsblk' to see all drives" -ForegroundColor White
    }
}

function Create-BootableDrive {
    param([string]$Device, [string]$IsoPath)
    
    Write-Host "`n⚠️  WARNING: This will DESTROY ALL DATA on $Device!" -ForegroundColor Red
    Write-Host "📀 Creating bootable drive..." -ForegroundColor Yellow
    Write-Host "   ISO File: $IsoPath" -ForegroundColor White
    Write-Host "   Target Device: $Device" -ForegroundColor White
    Write-Host ""
    
    # Confirm device exists
    if (-not (Test-Path $Device)) {
        Write-Host "❌ Error: Device $Device does not exist!" -ForegroundColor Red
        Write-Host "   Tip: Run 'lsblk' to see available devices" -ForegroundColor Yellow
        return
    }
    
    # Check if ISO exists
    if (-not (Test-Path $IsoPath)) {
        Write-Host "❌ Error: ISO file $IsoPath does not exist!" -ForegroundColor Red
        return
    }
    
    try {
        # Unmount any mounted partitions using Linux commands
        Write-Host "🔌 Unmounting any mounted partitions..." -ForegroundColor Yellow
        sudo umount ${Device}* 2>/dev/null
        
        # Write ISO to device using direct dd command
        Write-Host "💿 Writing ISO to device (this may take several minutes)..." -ForegroundColor Yellow
        Write-Host "   This will show progress updates..." -ForegroundColor Cyan
        
        # Use dd directly with sudo
        $result = & sudo dd if="$IsoPath" of="$Device" bs=4M status=progress conv=fsync 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Bootable USB created successfully!" -ForegroundColor Green
            Write-Host "💿 Device $Device is now bootable" -ForegroundColor Green
            Write-Host "   You can now use this USB drive to boot from" -ForegroundColor White
        } else {
            Write-Host "`n❌ Error creating bootable drive" -ForegroundColor Red
            Write-Host "   Error: $result" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

# ============================================
# FIXED: STORAGE FORMAT FUNCTIONS (Features 22-23) - LINUX COMPATIBLE
# ============================================

function Get-StorageDevices {
    Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    STORAGE DEVICES                            ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Use Linux lsblk command instead of Windows Get-Disk
    $disks = & lsblk -o NAME,SIZE,TYPE,MODEL -n 2>$null
    
    foreach ($line in $disks) {
        if ($line -match "disk") {
            $parts = $line -split '\s+', 4
            if ($parts.Count -ge 2) {
                $name = $parts[0]
                $size = $parts[1]
                $model = if ($parts.Count -ge 4) { $parts[3] } else { "Unknown" }
                
                Write-Host "💾 /dev/$name - ${size} - $model" -ForegroundColor Green
                
                # Show partitions for this disk using lsblk
                $partitions = & lsblk -o NAME,SIZE,TYPE,MOUNTPOINT -n "/dev/$name" 2>$null | Where-Object { $_ -match "part" }
                foreach ($part in $partitions) {
                    $partParts = $part -split '\s+', 4
                    if ($partParts.Count -ge 2) {
                        $partName = $partParts[0]
                        $partSize = $partParts[1]
                        $mountPoint = if ($partParts.Count -ge 4 -and $partParts[3]) { " (mounted at $($partParts[3]))" } else { "" }
                        Write-Host "   └─ /dev/$partName - ${partSize}$mountPoint" -ForegroundColor Gray
                    }
                }
                Write-Host ""
            }
        }
    }
}

function Format-Storage {
    param([string]$Device, [string]$Filesystem, [string]$Label)
    
    Write-Host "`n⚠️  WARNING: This will DESTROY ALL DATA on $Device!" -ForegroundColor Red
    Write-Host "💾 Formatting device..." -ForegroundColor Yellow
    Write-Host "   Device: $Device" -ForegroundColor White
    Write-Host "   Filesystem: $Filesystem" -ForegroundColor White
    if ($Label) { Write-Host "   Label: $Label" -ForegroundColor White }
    Write-Host ""
    
    # Check if device exists
    if (-not (Test-Path $Device)) {
        Write-Host "❌ Error: Device $Device does not exist!" -ForegroundColor Red
        Write-Host "   Tip: Run 'lsblk' to see available devices" -ForegroundColor Yellow
        return
    }
    
    # Check if device is a partition (has number) or full disk
    $isPartition = $Device -match '[0-9]+$'
    
    try {
        # Unmount if mounted (Linux command)
        Write-Host "🔌 Unmounting device if mounted..." -ForegroundColor Yellow
        sudo umount $Device 2>/dev/null
        
        # Format based on filesystem type using Linux mkfs commands
        Write-Host "💾 Formatting as $Filesystem..." -ForegroundColor Yellow
        
        $formatCmd = ""
        switch ($Filesystem) {
            "ext4" {
                if ($Label) {
                    $formatCmd = "sudo mkfs.ext4 -F -L `"$Label`" $Device"
                } else {
                    $formatCmd = "sudo mkfs.ext4 -F $Device"
                }
            }
            "ntfs" {
                if ($Label) {
                    $formatCmd = "sudo mkfs.ntfs -F -L `"$Label`" $Device"
                } else {
                    $formatCmd = "sudo mkfs.ntfs -F $Device"
                }
            }
            "fat32" {
                if ($Label) {
                    $formatCmd = "sudo mkfs.fat -F 32 -n `"$Label`" $Device"
                } else {
                    $formatCmd = "sudo mkfs.fat -F 32 $Device"
                }
            }
            "exfat" {
                if ($Label) {
                    $formatCmd = "sudo mkfs.exfat -n `"$Label`" $Device"
                } else {
                    $formatCmd = "sudo mkfs.exfat $Device"
                }
            }
            default {
                Write-Host "❌ Unsupported filesystem: $Filesystem" -ForegroundColor Red
                return
            }
        }
        
        # Execute the format command
        Invoke-Expression $formatCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Device formatted successfully as $Filesystem!" -ForegroundColor Green
            if ($Label) {
                Write-Host "🏷️  Volume label set to: $Label" -ForegroundColor Green
            }
        } else {
            Write-Host "❌ Format failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
}

# ============================================
# MAIN EXECUTION - CLI MODE
# ============================================

# If a feature number was provided, run it and exit
if ($Feature -gt 0) {
    switch ($Feature) {
        # Original features (1-12)
        1 { Show-SystemInfo }
        2 { Show-ProcessMonitor }
        3 { Show-RealtimeMonitor }
        4 { Show-NetworkInfo }
        5 { Show-Bandwidth }
        6 { Show-PortScan }
        7 { Show-ServiceManager }
        8 { Show-DiskAnalysis }
        9 { Show-CleanupTools }
        10 { Show-SecurityCheck }
        11 { Show-PackageUpdates }
        12 { Show-HardwareInfo }
        
        # File Manager features (13-19)
        13 { Get-FileList -Directory $Path }
        14 { Copy-ItemPS -Source $Source -Destination $Destination }
        15 { Move-ItemPS -Source $Source -Destination $Destination }
        16 { Delete-ItemPS -Path $Path }
        17 { Rename-ItemPS -Path $Path -NewName $Destination }
        18 { New-FolderPS -Path $Path }
        19 { Search-FilesPS -Directory $Path -Pattern $Destination -SearchContent:$SearchContent }
        
        # Bootable Drive features (20-21)
        20 { Get-USBDrives }
        21 { Create-BootableDrive -Device $Device -IsoPath $IsoPath }
        
        # Storage Format features (22-23)
        22 { Get-StorageDevices }
        23 { Format-Storage -Device $Device -Filesystem $Filesystem -Label $Label }
        
        default { Write-Host "Invalid feature number: $Feature" -ForegroundColor Red }
    }
    exit 0
}

# Otherwise, show the interactive menu
do {
    Show-Menu
    $choice = Read-Host "`n👉 Select an option (0-15)"
    
    switch ($choice) {
        "1" { Show-SystemInfo }
        "2" { Show-ProcessMonitor }
        "3" { Show-RealtimeMonitor }
        "4" { Show-NetworkInfo }
        "5" { Show-Bandwidth }
        "6" { Show-PortScan }
        "7" { Show-ServiceManager }
        "8" { Show-DiskAnalysis }
        "9" { Show-CleanupTools }
        "10" { Show-SecurityCheck }
        "11" { Show-PackageUpdates }
        "12" { Show-HardwareInfo }
        "13" { 
            $dir = Read-Host "Enter directory path"
            Get-FileList -Directory $dir
        }
        "14" { 
            Write-Host "`n=== BOOTABLE DRIVE CREATOR ===" -ForegroundColor Cyan
            Get-USBDrives
            $device = Read-Host "`nEnter device path (e.g., /dev/sdb)"
            $iso = Read-Host "Enter ISO file path"
            Create-BootableDrive -Device $device -IsoPath $iso
        }
        "15" { 
            Write-Host "`n=== STORAGE FORMATTER ===" -ForegroundColor Cyan
            Get-StorageDevices
            $device = Read-Host "`nEnter device path (e.g., /dev/sdb1)"
            $fs = Read-Host "Enter filesystem (ext4/ntfs/fat32/exfat)"
            $label = Read-Host "Enter volume label (optional)"
            Format-Storage -Device $device -Filesystem $fs -Label $label
        }
        "0" { 
            Write-Host "`n👋 Exiting Kali SmartOps Manager..." -ForegroundColor Yellow
            Write-Host "Thank you for using the tool!" -ForegroundColor Green
            break
        }
        default { 
            Write-Host "`n❌ Invalid option! Please choose 0-15" -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
    
    if ($choice -ne "0") {
        Write-Host "`n─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
        Write-Host "Press Enter to continue..."
        Read-Host
    }
} while ($choice -ne "0")
