<script>
    import axios from "axios";

    export default {
        methods: {
            async get(url) {
                try {
                    const response = await axios.get(url);
                    return await response.data;
                }
                catch (err) {
                    if (err.response && err.response.data && err.response.data.error && "Signage Orchestrator Backend" in err.response.data.error)
                        err = err.response.data.error["Signage Orchestrator Backend"]
                                        
                    throw new Error(err);
                }
            },

            async post(url, data) {  
                try {
                    const response = await axios.post(url, data); // data: auto-jsonify.
                    return await response.data;
                }
                catch (err) {
                    if (err.response && err.response.data && err.response.data.error && "Signage Orchestrator Backend" in err.response.data.error)
                        err = err.response.data.error["Signage Orchestrator Backend"]

                    throw new Error(err);
                }
            },              

            async patch(url, data) {  
                try {
                    const response = await axios.patch(url, data); // data: auto-jsonify.
                    return await response.data;
                }
                catch (err) {
                    if (err.response && err.response.data && err.response.data.error && "Signage Orchestrator Backend" in err.response.data.error)
                        err = err.response.data.error["Signage Orchestrator Backend"]

                    throw new Error(err);
                }
            },            

            async delete(url) {  
                try {
                    const response = await axios.delete(url);
                    return await response.data;
                }
                catch (err) {
                    if (err.response && err.response.data && err.response.data.error && "Signage Orchestrator Backend" in err.response.data.error)
                        err = err.response.data.error["Signage Orchestrator Backend"]

                    throw new Error(err);
                }
            }        
        }
    }
</script>
