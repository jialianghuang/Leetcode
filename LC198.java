class Solution {
        private HashMap<Integer, Integer> memo = new HashMap<Integer, Integer>();
        private int[]  nums;
        public int dp(int i){
            if(i==0) return nums[i];
            if(i==1) return Math.max(nums[0],nums[1]);
            if(!memo.containsKey(i))
            memo.put(i,Math.max(dp(i-1),dp(i-2)+nums[i]));
            return memo.get(i);
        }
        
    public int rob(int[] nums) {
        this.nums = nums;
        return dp(nums.length - 1);
    }
}
