import { createClient } from 'genlayer-js'
import { testnetBradbury } from 'genlayer-js/chains'
import { TransactionStatus } from 'genlayer-js/types'
import { ref } from 'vue'

export const CONTRACT_ADDRESS = import.meta.env.VITE_CONTRACT_ADDRESS as `0x${string}`

export const walletAddress = ref<string>('')
export const isConnected = ref(false)

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let _client: any = null

function buildClient(account: string) {
  return createClient({
    chain: testnetBradbury,
    account: account as `0x${string}`,
  })
}

export async function connectWallet(): Promise<string> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return _client as any
}

// Write contract with escalating-timeout retry loop (up to ~5 min total)
export async function writeWithRetry(
  functionName: string,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  args: any[],
  onHash?: (hash: string) => void,
  maxAttempts = 10,
) {
  const client = getClient()

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const hash = await client.writeContract({
    address: CONTRACT_ADDRESS,
    functionName,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    args: args as any,
    value: BigInt(0),
  })

  if (onHash) onHash(hash as string)

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const receipt = await (client.waitForTransactionReceipt as any)({
        hash,
        status: TransactionStatus.ACCEPTED,
        timeout: 30_000 * attempt,
      })
      return { hash, receipt }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      if (msg.includes('wallet_getSnaps')) continue
      if (attempt === maxAttempts) throw e
    }
  }
}

// Read contract (no gas)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function readContract(functionName: string, args: any[] = []) {
  const client = getClient()
  return client.readContract({
    address: CONTRACT_ADDRESS,
    functionName,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    args: args as any,
  })
}
