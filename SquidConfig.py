def write_config(proxies, file='squid.config'):
    template = 'cache_peer {ip} parent {port} no-query round-robin connect-fail-limit=2 allow-miss max-conn=5 name=proxy-{index}\n'
    with open(file, 'w') as f:
        for index, proxy in enumerate(proxies):
            ip, port = proxy.strip().split(':')
            if ip and port:
                f.write(template.format(ip=ip, port=port, index=index))
    print('All done!')


if __name__ == '__main__':
    with open('proxies.txt', 'r') as f:
        write_config(f)
