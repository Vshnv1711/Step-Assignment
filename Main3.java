public class Main3 {

    static void analyzeInventory(int[] sectionA, int[] sectionB) {

        int totalA = 0;
        int totalB = 0;

        // Calculate total of Section A
        for (int i = 0; i < sectionA.length; i++) {
            totalA += sectionA[i];
        }

        // Calculate total of Section B
        for (int i = 0; i < sectionB.length; i++) {
            totalB += sectionB[i];
        }

        String status;

        if (totalA == totalB) {
            status = "Balanced";
        } else {
            status = "Not Balanced";
        }

        // Find highest quantity
        int highest = sectionA[0];
        String highestSection = "Section A";
        int highestIndex = 0;

        // Check Section A
        for (int i = 1; i < sectionA.length; i++) {
            if (sectionA[i] > highest) {
                highest = sectionA[i];
                highestSection = "Section A";
                highestIndex = i;
            }
        }

        // Check Section B
        for (int i = 0; i < sectionB.length; i++) {
            if (sectionB[i] > highest) {
                highest = sectionB[i];
                highestSection = "Section B";
                highestIndex = i;
            }
        }

        System.out.println(
            "Section A Total: " + totalA +
            " | Section B Total: " + totalB +
            " | Status: " + status +
            " | Highest Quantity: " + highest +
            " (" + highestSection +
            ", Item " + (highestIndex + 1) + ")"
        );
    }

    public static void main(String[] args) {

        int[] sectionA = {20, 15, 30};
        int[] sectionB = {25, 10, 30};

        analyzeInventory(sectionA, sectionB);
    }
}