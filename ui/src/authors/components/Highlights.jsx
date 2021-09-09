import React, { useCallback } from 'react';
import PropTypes from 'prop-types';
import { HighlightOutlined } from '@ant-design/icons';
import { Button, Menu, Tooltip } from 'antd';
import { useParams } from 'react-router-dom';

import DropdownMenu from '../../common/components/DropdownMenu';
import IconText from '../../common/components/IconText';
import ListItemAction from '../../common/components/ListItemAction';

function Highlights({ onAssign, disabled }) {
  const currentAuthorId = Number(useParams().id);
  const onSelfAssign = useCallback(() => {
    onAssign({ from: currentAuthorId, to: currentAuthorId });
  }, [currentAuthorId, onAssign]);
  return (
    // TODO: rename `ListItemAction` because it's not only used for list item actions, such as (assign all and cite all)
    <ListItemAction>
      <DropdownMenu
        disabled={disabled}
        title={
          <Tooltip
            title={
              disabled
                ? 'Please select the papers you want to highlight.'
                : null
            }
          >
            <Button>
              <IconText text="highlight" icon={<HighlightOutlined />} />
            </Button>
          </Tooltip>
        }
      >
        <Menu.Item
          data-test-id="assign-self"
          key="assign-self"
          onClick={onSelfAssign}
        >
          Highlight this paper
        </Menu.Item>
      </DropdownMenu>
    </ListItemAction>
  );
}

Highlights.propTypes = {
  onAssign: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};

export default Highlights;
