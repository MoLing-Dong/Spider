import csv


def clean_csv(input_file, output_file, target_field):
    with open(input_file, 'r', encoding='utf-8', newline='') as infile, \
            open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            # 不手动添加引号，让 csv 模块自动处理
            writer.writerow(row)


if __name__ == "__main__":
    input_file = 'HScode.csv'
    output_file = 'output.csv'
    target_field = 'en_name'
    clean_csv(input_file, output_file, target_field)
