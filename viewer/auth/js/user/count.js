async function find_combination(target, numbers=[1, 2, 4, 8, 16, 32, 64, 128, 256, 512], index = 0, current_sum = 0, current_combination = [], result = []) {
  if (current_sum === target) {
      result.push([...current_combination]);
      return;
  }

  if (index >= numbers.length || current_sum > target) {
      return;
  }

  // 不选当前数字
  await find_combination(target, numbers, index + 1, current_sum, current_combination, result);

  // 选当前数字
  const new_sum = current_sum + numbers[index];
  const new_combination = [...current_combination, numbers[index]];
  await find_combination(target, numbers, index + 1, new_sum, new_combination, result);

  return result;
}

async function isin(TNumber, number=8) {
    combinations = await find_combination(TNumber);
    return combinations.some(combination => combination.includes(number))
}