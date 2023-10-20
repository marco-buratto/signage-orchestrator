<script>
    export default {
        methods: {
            toUnixTimestamp(d) {
                return Date.parse(d) / 1000; 
            }
        }
    }
</script>
