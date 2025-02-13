<script setup lang="ts">
import { computed, PropType } from "vue";
import { DocumentEntity } from "@/components/entity";
import DocumentSelect from "@/components/selects/DocumentSelect.vue";

const props = defineProps({
	entity: {
		type: Object as PropType<DocumentEntity>,
		required: true,
	},
	onlyOne: {
		type: Boolean,
	},
});
const entity = props.entity;

const error = computed(() => {
	if (entity.error.value) {
		return entity.error.value;
	}
});
</script>

<template>
	<div class="e-select">
		<span v-if="entity.withTitle" class="title">{{ entity.placeholder }}</span>
		<DocumentSelect
			:documents="entity.selectedEntities.value"
			:only-one="props.onlyOne"
			:placeholder="entity.placeholder"
			:required="entity.required"
			:readonly="entity.readonly"
			@submit="(docs) => entity.submit(docs)"
			@clear="() => entity.clear()"
			:error="error"
			:error-left-align="true"
		></DocumentSelect>
	</div>
</template>

<style scoped lang="scss">
@import "@/components/entity/entity.scss";
</style>
