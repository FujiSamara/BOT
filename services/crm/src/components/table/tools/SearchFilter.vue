<script setup lang="ts">
import DropDownMenu from "@/components/DropDownMenu.vue";
import EntitySelect from "@/components/entity/EntitySelect.vue";
import { BaseEntity, SelectType } from "@/components/entity";

const props = defineProps({
	style: {
		type: String,
	},
	alignRight: {
		type: Boolean,
	},
	entities: {
		type: Array<BaseEntity<any>>,
	},
});
</script>

<template>
	<DropDownMenu :style="props.style" :align-right="props.alignRight">
		<template #title>
			<div class="tool-icon-wrapper"><div class="tool-icon filter"></div></div>
			<span>Фильтры</span>
		</template>
		<template #menu>
			<EntitySelect
				v-for="entity in props.entities"
				:entity="entity"
				:select-type="SelectType.MultiSelectInput"
			></EntitySelect>
		</template>
	</DropDownMenu>
</template>

<style scoped lang="scss">
.tool-icon-wrapper {
	.tool-icon {
		width: 15px;
		height: 10px;

		&.filter {
			mask-image: url("@/assets/icons/filter.svg");
		}
	}
}
</style>
