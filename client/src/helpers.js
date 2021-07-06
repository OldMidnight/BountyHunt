function convertCents(amount) {
  /**
   * converts a monetary amount to cents
   * 
   * @param {money} amount The amount to convert]
   * @return {number} amount as cents
   */
  if (amount == null || amount === '') {
    return '';
  }
  const amount_list = (amount / 100).toString().split('.');

  if (amount_list.length > 1 && amount_list[1].length === 1) {
    amount_list[1] = amount_list[1] + '0'
  }

  return amount_list.join('.');
}

function relativeTime(previous) {
  /**
   * convert time to human readable format
   * 
   * @param {datetime} previous The reference timestamp
   * @returns {string} Human readable time string
   */

  const previousTime = new Date(previous)
  const currentTime = Date.now()

  const msPerMinute = 60 * 1000;
  const msPerHour = msPerMinute * 60;
  const msPerDay = msPerHour * 24;
  const msPerMonth = msPerDay * 30;
  const msPerYear = msPerDay * 365;

  const elapsed = currentTime - previousTime;
  
  if (elapsed < msPerMinute) {
    return Math.round(elapsed/1000) + ' seconds ago';
  } else if (elapsed < msPerHour) {
    return Math.round(elapsed/msPerMinute) + ' minutes ago';
  } else if (elapsed < msPerDay ) {
    return Math.round(elapsed/msPerHour ) + ' hours ago';
  } else if (elapsed < msPerMonth) {
    return Math.round(elapsed/msPerDay) + ' days ago';
  } else if (elapsed < msPerYear) {
    const month = Math.round(elapsed/msPerMonth);
    return month > 1 ?  `${month} months ago` : `${month} month ago`;   
  } else {
    return Math.round(elapsed/msPerYear ) + ' years ago';
  }
}

export { convertCents, relativeTime }