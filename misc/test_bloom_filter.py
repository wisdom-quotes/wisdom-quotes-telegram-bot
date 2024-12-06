from random import randint

from bloomfilter import BloomFilter

filter = BloomFilter(10000, 0.1)

result = {
}

total = 0
while True:
    attempt = 0
    picked = -1
    total = total + 1
    while attempt < 10:
        attempt = attempt + 1
        picked = randint(0, 10000)
        if not filter.might_contain("" + str(picked * 50)):
            break
        picked = -1
        print(f"Attempt: {attempt}")
    if picked == -1:
        break
    if picked in result:
        print("panic!")
        print(picked)
        print(result)
        exit(0)
        result[picked] = result[picked] + 1
    else:
        result[picked] = 1

    filter.put("" + str(picked * 50))
    print(total)

print(len(result))
print(len(filter.dumps_to_base64()))