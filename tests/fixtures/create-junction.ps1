param(
    [Parameter(Mandatory = $true)][string]$LinkPath,
    [Parameter(Mandatory = $true)][string]$TargetPath
)

$ErrorActionPreference = 'Stop'
try {
    New-Item -ItemType Junction -Path $LinkPath -Target $TargetPath | Out-Null
} catch {
    $taskError = $_.Exception.GetBaseException()
    if (($taskError -is [System.UnauthorizedAccessException]) -or
        (($taskError -is [System.ComponentModel.Win32Exception]) -and
         ($taskError.NativeErrorCode -in @(5, 1314)))) {
        Write-Error -Message 'Junction creation unavailable: access or privilege denied.' -ErrorAction Continue
        exit 77
    }
    throw
}
