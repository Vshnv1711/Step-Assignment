public class MovieReview {

    static void classifyWordLengths(String review) {

        String[] words = review.split(" ");

        int shortWords = 0;
        int mediumWords = 0;
        int longWords = 0;

        for (String word : words) {

            int len = word.length();

            if (len >= 1 && len <= 4)
                shortWords++;
            else if (len >= 5 && len <= 8)
                mediumWords++;
            else
                longWords++;
        }

        System.out.println("Short: " + shortWords);
        System.out.println("Medium: " + mediumWords);
        System.out.println("Long: " + longWords);
    }

    public static void main(String[] args) {

        classifyWordLengths("This movie was absolutely fantastic and thrilling");
    }
}