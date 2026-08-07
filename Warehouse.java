public class Warehouse {

    static void analyzeInventory(int[] sectionA, int[] sectionB) {

        int sumA = 0, sumB = 0;
        int max = Integer.MIN_VALUE;
        String section = "";
        int index = 0;

        for (int i = 0; i < sectionA.length; i++) {

            sumA += sectionA[i];
            sumB += sectionB[i];

            if (sectionA[i] > max) {
                max = sectionA[i];
                section = "Section A";
                index = i;
            }

            if (sectionB[i] > max) {
                max = sectionB[i];
                section = "Section B";
                index = i;
            }
        }

        System.out.println("Section A Total: " + sumA);
        System.out.println("Section B Total: " + sumB);

        if (sumA == sumB)
            System.out.println("Status: Balanced");
        else
            System.out.println("Status: Not Balanced");

        System.out.println("Highest Quantity: " + max + " (" + section +
                ", Item " + (index + 1) + ")");
    }

    public static void main(String[] args) {

        int[] sectionA = {20, 15, 30};
        int[] sectionB = {25, 10, 30};

        analyzeInventory(sectionA, sectionB);
    }
}