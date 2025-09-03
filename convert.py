import os
import re
import glob

def convert_conf_to_txt(conf_file, txt_file, cn_dns_list):
    """
    将 conf_file 中的域名列表转换成 AdGuardHome upstream_dns_file 格式，
    每个域名对所有 cn_dns_list 中的上游各写一行。
    """
    with open(conf_file, 'r', encoding='utf-8') as conf, \
         open(txt_file, 'w', encoding='utf-8') as txt:
        for line in conf:
            line = line.strip()
            if not line or '=' not in line:
                continue
            _, rhs = line.split('=', 1)
            if '/' not in rhs:
                continue
            domain = rhs.split('/')[1]
            # 每遇到一个域名，把列表里的每个上游都写一行
            for upstream in cn_dns_list:
                txt.write(f"[/{domain}/]{upstream}\n")

def main():
    # 读取环境变量
    cn_dns_raw = os.environ.get('CN_DNS', '')
    the_dns    = os.environ.get('THE_DNS', '')

    # 支持空格、换行、逗号分隔的多上游
    cn_dns_list = [u.strip() for u in re.split(r'[,\s]+', cn_dns_raw) if u.strip()]
    if not cn_dns_list:
        raise ValueError("环境变量 CN_DNS 未设置或为空！")

    current_directory = os.getcwd()
    converted_directory = os.path.join(current_directory, 'converted')
    os.makedirs(converted_directory, exist_ok=True)

    # 查找待处理文件
    conf_files = glob.glob(os.path.join(current_directory, '*china.conf'))

    for conf_file in conf_files:
        if os.path.basename(conf_file) == 'bogus-nxdomain.china.conf':
            continue
        txt_file = os.path.join(converted_directory,
                                os.path.basename(conf_file) + '.txt')
        convert_conf_to_txt(conf_file, txt_file, cn_dns_list)

    # 合并所有 txt 到 FAK-DNS.txt
    txt_files = glob.glob(os.path.join(converted_directory, '*conf.txt'))
    with open(os.path.join(converted_directory, 'FAK-DNS.txt'), 'w', encoding='utf-8') as fak_dns:
        fak_dns.write(the_dns + "\n")
        for txt_file in txt_files:
            with open(txt_file, 'r', encoding='utf-8') as src:
                fak_dns.write(src.read())

if __name__ == '__main__':
    main()