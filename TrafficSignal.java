public class TrafficSignal {

    static void findLongestStreak(String signalLog) {

        char maxColor = signalLog.charAt(0);
        int maxCount = 1;
        int count = 1;

        for (int i = 1; i < signalLog.length(); i++) {

            if (signalLog.charAt(i) == signalLog.charAt(i - 1))
                count++;
            else
                count = 1;

            if (count > maxCount) {
                maxCount = count;
                maxColor = signalLog.charAt(i);
            }
        }

        System.out.println("Longest Streak: '" + maxColor +
                "' repeated " + maxCount + " times");
    }

    public static void main(String[] args) {
        findLongestStreak("RRGGGYRR");
    }
}