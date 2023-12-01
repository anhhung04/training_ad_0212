import os
import re
import string

base_dockerfile = """\
FROM alpine:latest

RUN apk add iptables \
    openssh \
    curl \
    git \
    sudo \

RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

RUN adduser -h /home/ctf_player -s /bin/sh -D ctf_player

RUN echo  "ctf_player:%s" | chpasswd

RUN echo "ctf_player ALL=(ALL) ALL" > /etc/sudoers.d/ctf_player && chmod 0440 /etc/sudoers.d/ctf_player

RUN echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf \
    && sysctl -p \

# Configure port forwarding
RUN echo -ne %s > /entrypoint.sh 

RUN chmod +x /entrypoint.sh

EXPOSE 22

WORKDIR /app

CMD ["/entrypoint.sh"]
"""

entrypoint = """"#!/bin/sh
set -e
%s
ssh-keygen -A
exec /usr/sbin/sshd -D -e "$@"
" """.replace("\n", "\\n")

ports = []

if __name__ == "__main__":
    team_id = int(input("Enter team id: "))
    alp = string.ascii_lowercase + string.ascii_uppercase + string.digits
    proxy_password = input("Enter proxy password: ")
    services = os.listdir("./services")
    
    ip_forward_service_config = ""
    
    try:
        os.system(f"docker network create training_ad")
    except Exception as e:
        print(e)
    
    for i in range(len(services)):
        service = services[i]
        service_port = re.findall(r"(\d+:\d+)", open(f"./services/{service}/docker-compose.yml").read())[0].split(":")[1]
        coming_port = re.findall(r"(\d+:\d+)", open(f"./services/{service}/docker-compose.yml").read())[0].split(":")[0]
        if "/udp" in service_port:
            ports.append("-p %s:%s " % (coming_port, coming_port + "/udp"))
        else:
            ports.append("-p %s:%s " % (coming_port, coming_port))
        proto = "udp" if "/udp" in service_port else "tcp"
        ip_forward_service_config += "service_%d_ip=\$(nslookup %s | awk '/^Address: / { print \$2 }')\n" % (i+1, service)
        ip_forward_service_config += f"iptables -t nat -A PREROUTING -p {proto} --dport {coming_port} -j DNAT --to-destination \$service_{str(i+1)}_ip:{service_port}\n"
        ip_forward_service_config += f"iptables -t nat -A POSTROUTING -j MASQUERADE\n"

        print("[+] Composing service %s" % service)
        try:
            os.system(f"docker compose -f ./services/{service}/docker-compose.yml up -d")
        except:
            print("[-] Error while composing service %s" % service)
            continue
    print('[+] Creating proxy')
    try:
        entrypoint = (entrypoint % ip_forward_service_config)
        entrypoint = entrypoint.replace("\n", "\\n")
        dockerfile_content = (base_dockerfile % (proxy_password, entrypoint))
        open("Dockerfile.tmp", "w").write(dockerfile_content)
        os.system(f'docker build -t proxy_{team_id} -f Dockerfile.tmp .')
        os.unlink("Dockerfile.tmp")
    except Exception as e:
        print(e)
        print("[-] Error while creating proxy")
        exit(1)
    try:
        ports = "".join(ports)
        os.system(f"docker run -p2222:22 {ports} --cap-add NET_ADMIN --name proxy_{team_id} --net training_ad -d proxy_{team_id}")
    except Exception as e:
        print(e)
        print("[-] Error while running proxy")
        exit(1)
