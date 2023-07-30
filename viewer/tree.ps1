param (
    [string]$Path = (Get-Location).Path,
    [int]$Level = -1
)

function Get-Tree {
    param (
        [string]$Path,
        [int]$IndentLevel = 0,
        [int]$Level = -1
    )

    $indent = "| " * $IndentLevel

    # 获取目录列表
    $items = Get-ChildItem -Path $Path

    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            # 打印目录
            Write-Host ("{0}{1}" -f $indent, $item.Name)

            if ($Level -ne 0) {
                # 递归调用 Get-Tree 函数
                Get-Tree -Path $item.FullName -IndentLevel ($IndentLevel + 1) -Level ($Level - 1)
            }
        }
        else {
            # 打印文件
            Write-Host ("{0}{1}" -f $indent, $item.Name)
        }
    }
}

# 使用示例
Get-Tree -Path $Path -Level $Level
