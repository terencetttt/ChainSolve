import { createClient } from 'genlayer-js'
import { testnetBradbury } from 'genlayer-js/chains'
import { TransactionStatus } from 'genlayer-js/types'
import { ref } from 'vue'

export const CONTRACT_ADDRESS = import.meta.env.VITE_CONTRACT_ADDRESS as `0x${string}`

export const walletAddress = ref<string>('')
export const isConnected = ref(false)

let _client: ReturnType<typeof createClient> | null = null

function buildClient(account: string) {
  return createClient({
    chain: testnetBradbury,
    account: account as `0x${string}`,
  })
}

export async function connectWallet(): Promise<string> {
  const eth = (window as any).ethereum
  if (!eth) throw new Error('No wallet detected. Please install Rabby or MetaMask.')
  const accounts: string[] = await eth.request({ method: 'eth_requestAccounts' })
  walletAddress.value = accounts[0]
  isConnected.value = true
  _client = buildClient(accounts[0])
  await _client.connect('testnetBradbury')
  return walletAddress.value
}

export function getClient() {
  if (!_client) throw new Error('Wallet not connected')
  return _client
}

// Write contract with escalating-timeout retry loop (up to ~5 min total)
export async function writeWithRetry(
  functionName: string,
  args: unknown[],
  onHash?: (hash: string) => void,
  maxAttempts = 10,
) {
  const client = getClient()

  const hash = await client.writeContract({
    address: CONTRACT_ADDRESS,
    functionName,
    args,
    value: BigInt(0),
  })

  if (onHash) onHash(hash as string)

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const receipt = await client.waitForTransactionReceipt({
        hash,
        status: TransactionStatus.ACCEPTED,
        timeout: 30_000 * attempt, // 30s, 60s, 90s …
      })
      return { hash, receipt }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      if (msg.includes('wallet_getSnaps')) continue // harmless Rabby noise
      if (attempt === maxAttempts) throw e
    }
  }
}

// Read contract (no gas)
export async function readContract(functionName: string, args: unknown[] = []) {
  const client = getClient()
  return client.readContract({
    address: CONTRACT_ADDRESS,
    functionName,
    args,
  })
}
