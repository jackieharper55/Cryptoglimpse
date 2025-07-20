import requests
import statistics
import time
from datetime import datetime

ETHERSCAN_API_KEY = 'YourEtherscanAPIKeyHere'  # Вставь свой API ключ

def get_latest_transactions(address="0x0000000000000000000000000000000000000000", limit=50):
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&sort=desc&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data['status'] != '1':
        print("Ошибка получения транзакций.")
        return []

    return data['result'][:limit]

def analyze_transactions(transactions):
    values = [int(tx['value']) / 1e18 for tx in transactions if int(tx['value']) > 0]
    gas_prices = [int(tx['gasPrice']) / 1e9 for tx in transactions]

    anomalies = []

    if not values or not gas_prices:
        return anomalies

    mean_val = statistics.mean(values)
    std_val = statistics.stdev(values)

    mean_gas = statistics.mean(gas_prices)
    std_gas = statistics.stdev(gas_prices)

    for tx in transactions:
        eth_value = int(tx['value']) / 1e18
        gas_price = int(tx['gasPrice']) / 1e9

        if eth_value > mean_val + 2 * std_val or gas_price > mean_gas + 2 * std_gas:
            anomalies.append({
                'hash': tx['hash'],
                'from': tx['from'],
                'to': tx['to'],
                'value_eth': eth_value,
                'gas_price_gwei': gas_price,
                'time': datetime.utcfromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')
            })

    return anomalies

def main():
    # Пример адреса — Tether (USDT)
    address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    print(f"🔍 Анализ транзакций для: {address}")

    transactions = get_latest_transactions(address)

    anomalies = analyze_transactions(transactions)

    print(f"\n📈 Найдено аномалий: {len(anomalies)}")
    for a in anomalies:
        print(f"- [{a['time']}] {a['value_eth']} ETH | From: {a['from']} → To: {a['to']} | Gas: {a['gas_price_gwei']} Gwei\n  TxHash: {a['hash']}\n")

if __name__ == "__main__":
    while True:
        main()
        print("⏳ Ждём следующего цикла...\n")
        time.sleep(60)  # анализ каждые 60 секунд
